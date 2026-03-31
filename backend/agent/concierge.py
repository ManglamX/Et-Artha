# agent/concierge.py
import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from agent.prompts import CONCIERGE_SYSTEM_PROMPT, PROFILE_EXTRACTION_PROMPT, RECOMMENDATION_PROMPT
from agent.triggers import check_triggers
from knowledge.retriever import retrieve_for_profile, format_products_for_prompt
import httpx

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "et-artha"  # Latika's fine-tuned model


class AgentState(TypedDict):
    messages: list[dict]           # full conversation history
    turn_count: int                # how many turns so far
    profile: dict | None           # extracted user profile
    recommendations: list[dict]    # final recommendations
    profile_complete: bool         # has profiling finished?
    trigger_fired: str | None      # cross-sell trigger that fired


class ConciergeAgent:
    def __init__(self, session: dict):
        """
        session: dict from Manglam's database.get_session()
        Contains: session_id, messages, profile, recommendations
        """
        self.session = session
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("respond", self._respond_node)
        workflow.add_node("extract_profile", self._extract_profile_node)
        workflow.add_node("recommend", self._recommend_node)

        # After responding, check if we should extract profile
        workflow.add_conditional_edges(
            "respond",
            self._should_extract,
            {
                "extract": "extract_profile",
                "continue": END,
            }
        )
        # After extracting, always recommend
        workflow.add_edge("extract_profile", "recommend")
        workflow.add_edge("recommend", END)

        workflow.set_entry_point("respond")
        return workflow.compile()

    def _should_extract(self, state: AgentState) -> str:
        """Extract profile after 4+ turns, or if model signals readiness."""
        if state["turn_count"] >= 4 and not state["profile_complete"]:
            return "extract"
        return "continue"

    async def _call_ollama(self, prompt: str, system: str = None) -> str:
        """Call Ollama's local model."""
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 512}
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            r.raise_for_status()
            return r.json()["response"]

    async def _respond_node(self, state: AgentState) -> AgentState:
        """Generate ET Artha's next conversational response."""
        messages = state["messages"]

        # Check cross-sell triggers on last user message
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        trigger = check_triggers(last_user_msg)
        trigger_addition = ""
        if trigger:
            trigger_addition = f"\n\nAlso mention naturally: {trigger['message']}"

        # Build conversation history for prompt
        history = "\n".join([
            f"{'User' if m['role'] == 'user' else 'ET Artha'}: {m['content']}"
            for m in messages[-8:]
        ])

        prompt = f"""Conversation history:
{history}

ET Artha:{trigger_addition}"""

        response = await self._call_ollama(prompt, system=CONCIERGE_SYSTEM_PROMPT)

        messages.append({"role": "assistant", "content": response})

        return {
            **state,
            "messages": messages,
            "turn_count": state["turn_count"] + 1,
            "trigger_fired": trigger["product"] if trigger else None,
        }

    async def _extract_profile_node(self, state: AgentState) -> AgentState:
        """Extract structured UserProfile JSON from conversation."""
        conversation_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in state["messages"]
        ])

        prompt = PROFILE_EXTRACTION_PROMPT.format(conversation=conversation_text)
        response = await self._call_ollama(prompt)

        try:
            # Extract JSON from response (model might add some text around it)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                profile = json.loads(response[json_start:json_end])
            else:
                profile = {"archetype": "THE CURIOUS LEARNER", "profession": "unknown", "experience": "beginner", "goal": "learn about investing", "interests": [], "profile_confidence": 0.5}
        except json.JSONDecodeError:
            profile = {"archetype": "THE CURIOUS LEARNER", "profession": "unknown", "experience": "beginner", "goal": "learn about investing", "interests": [], "profile_confidence": 0.5}

        return {**state, "profile": profile, "profile_complete": True}

    async def _recommend_node(self, state: AgentState) -> AgentState:
        """Generate personalized ET product recommendations."""
        profile = state["profile"]

        # RAG: retrieve relevant products from ChromaDB
        relevant_products = retrieve_for_profile(profile, n_results=6)
        products_context = format_products_for_prompt(relevant_products)

        prompt = RECOMMENDATION_PROMPT.format(
            profile=json.dumps(profile, indent=2),
            products_context=products_context
        )

        response = await self._call_ollama(prompt)

        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            data = json.loads(response[json_start:json_end])
            recommendations = data.get("recommendations", [])
        except:
            recommendations = []

        return {**state, "recommendations": recommendations}

    async def process(self, user_message: str) -> dict:
        """
        Main entry point called by Manglam's FastAPI route.
        Returns: {
            "response": str,           — ET Artha's reply
            "profile": dict | None,    — user profile if ready
            "recommendations": list,   — recommendations if ready
        }
        """
        # Load current state from session
        initial_state: AgentState = {
            "messages": self.session.get("messages", []) + [{"role": "user", "content": user_message}],
            "turn_count": len([m for m in self.session.get("messages", []) if m["role"] == "user"]) + 1,
            "profile": self.session.get("profile"),
            "recommendations": self.session.get("recommendations", []),
            "profile_complete": self.session.get("profile") is not None,
            "trigger_fired": None,
        }

        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)

        # Get latest assistant response
        last_response = next(
            (m["content"] for m in reversed(final_state["messages"]) if m["role"] == "assistant"), ""
        )

        return {
            "response": last_response,
            "messages": final_state["messages"],
            "profile": final_state.get("profile"),
            "recommendations": final_state.get("recommendations", []),
            "profile_complete": final_state.get("profile_complete", False),
        }
