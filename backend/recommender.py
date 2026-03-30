# backend/recommender.py
"""
Recommendation engine: UserProfile → ET product recommendations.

Strategy:
  1. Archetype-based priority rules   (always present, guaranteed quality)
  2. RAG supplement via ChromaDB      (Anuj's retriever, if available)
  3. Deduplicate → return top N
"""

from __future__ import annotations

# ── ET product catalogue ────────────────────────────────────────────────────

ET_PRODUCTS = {
    "ET Prime": {
        "url": "https://economictimes.indiatimes.com/prime",
        "cta": "Start 30-day free trial",
        "category": "content",
    },
    "ET Markets": {
        "url": "https://economictimes.indiatimes.com/markets",
        "cta": "Track markets free",
        "category": "finance",
    },
    "ET Wealth": {
        "url": "https://economictimes.indiatimes.com/wealth",
        "cta": "Plan your finances free",
        "category": "finance",
    },
    "ET Masterclass": {
        "url": "https://etmasterclass.economictimes.com",
        "cta": "View upcoming masterclasses",
        "category": "education",
    },
    "ET Edge Summits": {
        "url": "https://etedge.economictimes.com",
        "cta": "See upcoming summits",
        "category": "events",
    },
    "ET Entrepreneur Summit": {
        "url": "https://economictimes.indiatimes.com/small-biz",
        "cta": "Register for next summit",
        "category": "events",
    },
    "ET Money": {
        "url": "https://www.etmoney.com",
        "cta": "Start SIP with ₹500",
        "category": "services",
    },
    "ET Now": {
        "url": "https://etnow.com",
        "cta": "Watch live for free",
        "category": "content",
    },
    "ET Portfolio": {
        "url": "https://economictimes.indiatimes.com/markets/portfolio",
        "cta": "Track your portfolio free",
        "category": "finance",
    },
    # Discovered in training_data.json — used for THE CAREFUL PLANNER
    "ET Fixed Deposit Tracker": {
        "url": "https://economictimes.indiatimes.com/wealth/invest/fixed-deposit",
        "cta": "Compare FD rates",
        "category": "services",
    },
}


# ── Archetype → priority recommendation list ────────────────────────────────

ARCHETYPE_PRIORITY_MAP: dict[str, list[dict]] = {
    "THE MARKET MAVERICK": [
        {
            "product": "ET Markets",
            "reason": "Live Nifty/Sensex prices, F&O data, and stock screener — built for active traders",
            **ET_PRODUCTS["ET Markets"],
            "priority": 1,
        },
        {
            "product": "ET Prime",
            "reason": "In-depth market analysis and expert trading views published every morning",
            **ET_PRODUCTS["ET Prime"],
            "priority": 2,
        },
        {
            "product": "ET Now",
            "reason": "Live market commentary during trading hours from ET's market experts",
            **ET_PRODUCTS["ET Now"],
            "priority": 3,
        },
        {
            "product": "ET Portfolio",
            "reason": "Track all your F&O and equity positions in one place with real-time P&L",
            **ET_PRODUCTS["ET Portfolio"],
            "priority": 4,
        },
    ],
    "THE WEALTH BUILDER": [
        {
            "product": "ET Wealth",
            "reason": "Best beginner-to-intermediate guides on SIPs, goal-based investing, and tax planning",
            **ET_PRODUCTS["ET Wealth"],
            "priority": 1,
        },
        {
            "product": "ET Money",
            "reason": "Direct mutual fund plans with 0% commission — you keep every rupee of returns",
            **ET_PRODUCTS["ET Money"],
            "priority": 2,
        },
        {
            "product": "ET Prime",
            "reason": "Weekend reads on personal finance, market trends, and investment strategy",
            **ET_PRODUCTS["ET Prime"],
            "priority": 3,
        },
    ],
    "THE CORNER OFFICE": [
        {
            "product": "ET Prime",
            "reason": "Deep policy analysis, M&A coverage, and global macro insights for senior leaders",
            **ET_PRODUCTS["ET Prime"],
            "priority": 1,
        },
        {
            "product": "ET Masterclass",
            "reason": "Executive workshops by PwC, KPMG, and IIM faculty on finance and leadership",
            **ET_PRODUCTS["ET Masterclass"],
            "priority": 2,
        },
        {
            "product": "ET Edge Summits",
            "reason": "Industry-specific conferences where sector CXOs network and set the agenda",
            **ET_PRODUCTS["ET Edge Summits"],
            "priority": 3,
        },
    ],
    "THE STARTUP SHERPA": [
        {
            "product": "ET Entrepreneur Summit",
            "reason": "Best event to meet Series A/B investors and fellow founders building at your stage",
            **ET_PRODUCTS["ET Entrepreneur Summit"],
            "priority": 1,
        },
        {
            "product": "ET Prime",
            "reason": "Startup funding news, policy for startups, and VC perspectives — all in one place",
            **ET_PRODUCTS["ET Prime"],
            "priority": 2,
        },
        {
            "product": "ET Masterclass",
            "reason": "Finance and strategy workshops relevant for founders building scalable businesses",
            **ET_PRODUCTS["ET Masterclass"],
            "priority": 3,
        },
    ],
    "THE CAREFUL PLANNER": [
        {
            "product": "ET Wealth",
            "reason": "Guides on FD laddering, NPS, and retirement corpus planning for conservative investors",
            **ET_PRODUCTS["ET Wealth"],
            "priority": 1,
        },
        {
            "product": "ET Fixed Deposit Tracker",
            "reason": "Compare best FD rates across banks for maximum safe returns on your corpus",
            **ET_PRODUCTS["ET Fixed Deposit Tracker"],
            "priority": 2,
        },
        {
            "product": "ET Money",
            "reason": "Debt fund investments with zero commission for better post-tax returns than FDs",
            **ET_PRODUCTS["ET Money"],
            "priority": 3,
        },
    ],
    "THE CURIOUS LEARNER": [
        {
            "product": "ET Wealth",
            "reason": "Easy-to-understand financial literacy guides — perfect for building foundational knowledge",
            **ET_PRODUCTS["ET Wealth"],
            "priority": 1,
        },
        {
            "product": "ET Money",
            "reason": "Start your first SIP with as little as ₹500 — guided, simple, and commission-free",
            **ET_PRODUCTS["ET Money"],
            "priority": 2,
        },
        {
            "product": "ET Markets",
            "reason": "Free portfolio tracker and market education tools — learn by watching live markets",
            **ET_PRODUCTS["ET Markets"],
            "priority": 3,
        },
    ],
}


# ── Main recommendation function ─────────────────────────────────────────────

def get_recommendations(profile: dict, max_recs: int = 4) -> list[dict]:
    """
    Return personalised ET product recommendations for a given UserProfile.

    Args:
        profile:   UserProfile dict (output of Anuj's extractor / archetype.validate_and_fix_profile)
        max_recs:  Maximum number of recommendations to return (default 4)

    Returns:
        List of recommendation dicts, each with: product, reason, cta, url, priority, category
    """
    archetype = profile.get("archetype", "THE CURIOUS LEARNER")

    # 1. Seed with archetype rules (always present)
    base_recs: list[dict] = list(
        ARCHETYPE_PRIORITY_MAP.get(archetype, ARCHETYPE_PRIORITY_MAP["THE CURIOUS LEARNER"])
    )

    # 2. Try RAG supplement (Anuj's ChromaDB retriever)
    try:
        from knowledge.retriever import retrieve_for_profile  # Anuj's module

        rag_items = retrieve_for_profile(profile, n_results=4)
        seen_products = {r["product"] for r in base_recs}

        for item in rag_items:
            if item["name"] not in seen_products:
                base_recs.append(
                    {
                        "product": item["name"],
                        "reason": _personalize_reason(item, profile),
                        "cta": item.get("cta", "Learn more"),
                        "url": item.get("url", ""),
                        "priority": len(base_recs) + 1,
                        "category": item.get("category", "content"),
                    }
                )
                seen_products.add(item["name"])

    except Exception as exc:
        # RAG is optional — gracefully fall back to archetype rules only
        print(f"[recommender] RAG retrieval skipped: {exc}")

    return base_recs[:max_recs]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _personalize_reason(item: dict, profile: dict) -> str:
    """Build a personalised reason string from a RAG-retrieved item."""
    profession = profile.get("profession", "")
    goal = profile.get("goal", "")
    desc = item.get("document", "")[:120]

    # 'unknown' profession appears in training_data — skip it for personalisation
    if profession and profession.lower() not in ("", "unknown"):
        return f"Given your background in {profession} — {desc}..."
    if goal:
        return f"Aligns with your goal to {goal} — {desc}..."
    return desc + "..."


def format_recommendations_for_llm(recs: list[dict]) -> str:
    """
    Stringify recommendations so the LangGraph agent can embed them in a prompt.
    """
    lines = []
    for r in recs:
        lines.append(
            f"{r['priority']}. **{r['product']}** — {r['reason']}\n"
            f"   👉 {r['cta']}: {r['url']}"
        )
    return "\n".join(lines)


# ── quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Profiles directly from training_data.json to verify alignment
    sample_profiles = [
        {
            "archetype": "THE MARKET MAVERICK",
            "profession": "trader",
            "experience": "intermediate",
            "goal": "improve trading decisions and market timing",
            "interests": ["Nifty", "F&O", "intraday", "market analysis"],
            "profile_confidence": 0.9,
        },
        {
            "archetype": "THE WEALTH BUILDER",
            "profession": "software engineer",
            "experience": "beginner",
            "goal": "long term wealth and tax saving",
            "interests": ["SIP", "mutual funds", "ELSS", "tax saving"],
            "profile_confidence": 0.88,
        },
        {
            "archetype": "THE CORNER OFFICE",
            "profession": "CEO",
            "experience": "expert",
            "goal": "stay informed on macro and lead digital transformation",
            "interests": ["macro", "policy", "leadership", "digital transformation"],
            "profile_confidence": 0.95,
        },
        {
            "archetype": "THE STARTUP SHERPA",
            "profession": "SaaS founder",
            "experience": "beginner",
            "goal": "connect with VCs and validate market opportunity",
            "interests": ["startup", "VC", "funding", "SaaS"],
            "profile_confidence": 0.87,
        },
        {
            "archetype": "THE CAREFUL PLANNER",
            "profession": "unknown",   # appears in training data — must handle gracefully
            "experience": "intermediate",
            "goal": "protect retirement corpus with safe instruments",
            "interests": ["FD", "PPF", "retirement", "capital protection"],
            "profile_confidence": 0.9,
        },
        {
            "archetype": "THE CURIOUS LEARNER",
            "profession": "student",
            "experience": "beginner",
            "goal": "learn safe investing and grow savings",
            "interests": ["financial literacy", "investing basics", "stock market"],
            "profile_confidence": 0.85,
        },
    ]

    for profile in sample_profiles:
        print(f"\n{'='*60}")
        print(f"Archetype : {profile['archetype']}  |  Profession: {profile['profession']}")
        recs = get_recommendations(profile, max_recs=3)
        for r in recs:
            print(f"  [{r['priority']}] {r['product']} — {r['reason'][:70]}...")
        print()
        print(format_recommendations_for_llm(recs))
