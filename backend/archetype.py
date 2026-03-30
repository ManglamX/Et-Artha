# backend/archetype.py
"""
Rule-based archetype classifier as a fast deterministic fallback.
Used when LLM profile extraction returns low confidence.
"""

from dataclasses import dataclass


@dataclass
class ArchetypeScore:
    archetype: str
    score: float
    signals: list[str]  # what triggered this score


ARCHETYPE_SIGNALS = {
    "THE MARKET MAVERICK": {
        "keywords": [
            "trade", "trading", "nifty", "sensex", "stocks", "f&o", "options", "futures",
            "intraday", "swing", "technical analysis", "demat", "broker", "equity",
            "momentum", "screener", "otm", "market open", "pre-market", "chart",
        ],
        "professions": ["trader", "broker", "fund manager", "analyst"],
        "weight": 1.0,
    },
    "THE WEALTH BUILDER": {
        "keywords": [
            "sip", "mutual fund", "invest", "goal", "wealth", "portfolio", "elss",
            "long term", "retirement", "savings", "returns", "compounding",
            "tax saving", "80c", "nps", "goal-based", "large cap", "mid cap",
            "child education", "sukanya", "direct plan", "regular plan",
        ],
        "professions": ["engineer", "doctor", "teacher", "professional", "employee", "salaried"],
        "weight": 1.0,
    },
    "THE CORNER OFFICE": {
        "keywords": [
            "cfo", "ceo", "cto", "cxo", "director", "vp", "head of", "president",
            "macro", "policy", "strategy", "m&a", "corporate", "global", "board",
            "geopolitics", "supply chain", "digital transformation", "listed company",
            "leadership", "executive education", "fortune 500",
        ],
        "professions": ["cfo", "ceo", "vp", "director", "head", "senior", "president", "executive"],
        "weight": 1.0,
    },
    "THE STARTUP SHERPA": {
        "keywords": [
            "startup", "founder", "co-founder", "venture", "vc", "angel", "seed",
            "series a", "fundraising", "pitch", "product", "scale", "entrepreneur",
            "d2c", "saas", "pre-revenue", "pilots", "market sizing", "arr",
            "unit economics", "investors", "ecosystem",
        ],
        "professions": ["founder", "co-founder", "entrepreneur", "startup", "cto of startup", "saas founder"],
        "weight": 1.0,
    },
    "THE CAREFUL PLANNER": {
        "keywords": [
            "fd", "fixed deposit", "safe", "conservative", "risk averse", "insurance",
            "retire", "pension", "ppf", "guaranteed", "protect", "secure",
            "corpus", "nps", "debt fund", "bonds", "capital protection", "nbfc",
            "7.5%", "laddering", "senior citizen",
        ],
        "professions": ["retired", "near retirement", "government", "senior government"],
        "weight": 1.0,
    },
    "THE CURIOUS LEARNER": {
        "keywords": [
            "student", "just started", "beginner", "new to", "learning", "first time",
            "understand", "how does", "explain", "basics", "college",
            "no idea", "first job", "first sip", "financially smart", "emergency fund",
        ],
        "professions": ["student", "fresher", "intern", "recent graduate"],
        "weight": 1.0,
    },
}


def classify_archetype(conversation_text: str, profession: str = "") -> ArchetypeScore:
    """
    Classify user into one of 6 ET financial archetypes.
    Returns the best matching archetype with its score and matched signals.
    """
    text = (conversation_text + " " + profession).lower()

    scores: dict[str, float] = {}
    signals: dict[str, list[str]] = {}

    for archetype, config in ARCHETYPE_SIGNALS.items():
        score = 0.0
        matched_signals: list[str] = []

        # Check keywords in the conversation text
        for kw in config["keywords"]:
            if kw in text:
                score += 1.0 * config["weight"]
                matched_signals.append(f"keyword: '{kw}'")

        # Profession keywords carry higher weight
        for prof in config["professions"]:
            if prof in profession.lower():
                score += 2.0 * config["weight"]
                matched_signals.append(f"profession: '{prof}'")

        scores[archetype] = score
        signals[archetype] = matched_signals

    if not any(scores.values()):
        # Nothing matched — default to the safest archetype
        return ArchetypeScore("THE CURIOUS LEARNER", 0.0, ["default: no signals matched"])

    best_archetype = max(scores, key=scores.get)
    return ArchetypeScore(
        archetype=best_archetype,
        score=scores[best_archetype],
        signals=signals[best_archetype],
    )


def validate_and_fix_profile(profile: dict, conversation: str = "") -> dict:
    """
    Validate an LLM-extracted profile dict.
    If confidence < 0.6, override the archetype with the rule-based classifier.
    Handles 'unknown' profession and 'expert' experience seen in training_data.
    """
    if not profile:
        return _default_profile()

    confidence = profile.get("profile_confidence", 0.5)

    if confidence < 0.6:
        profession = profile.get("profession", "")
        # Skip 'unknown' for classification — it adds no signal
        clean_profession = "" if profession.lower() == "unknown" else profession
        result = classify_archetype(conversation, clean_profession)
        profile["archetype"] = result.archetype
        profile["classification_method"] = "rule_based"
        profile["classification_signals"] = result.signals
    else:
        profile["classification_method"] = "llm_extracted"

    # Guarantee required fields always exist
    profile.setdefault("profession", "professional")
    profile.setdefault("experience", "intermediate")
    profile.setdefault("goal", "stay informed and grow wealth")
    profile.setdefault("interests", [])

    # Normalise experience: training_data uses 'expert' — map to 'advanced' for consistency
    exp_map = {"expert": "advanced", "expert level": "advanced"}
    profile["experience"] = exp_map.get(profile["experience"].lower(), profile["experience"])

    return profile


def _default_profile() -> dict:
    return {
        "archetype": "THE CURIOUS LEARNER",
        "profession": "professional",
        "experience": "beginner",
        "goal": "learn about personal finance",
        "interests": [],
        "profile_confidence": 0.3,
        "classification_method": "default",
    }


# ── quick smoke-test ────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test cases derived from actual training_data.json conversations
    tests = [
        # (conversation_snippet, profession)
        ("I trade Nifty options every day, intraday only. I use momentum screeners.", "trader"),
        ("I just started my first SIP last month. Want to save tax via 80C.", "software engineer"),
        ("I'm the CFO of a mid-size pharma. I follow macro and M&A closely.", "CFO"),
        ("We just closed our seed round. Building a SaaS startup, pre-revenue, 10 pilots.", "SaaS founder"),
        ("I'm risk-averse. All savings in FDs and PPF. Retiring in 3 years.", "senior government employee"),
        ("I'm completely new to investing. No idea where to begin.", "student"),
        # Edge cases found in training_data
        ("I want to protect my corpus.", "unknown"),     # 'unknown' profession
        ("I lead digital transformation at a Fortune 500.", "CEO"),  # 'expert' experience
    ]

    for conv, prof in tests:
        result = classify_archetype(conv, prof)
        print(f"Input     : {conv[:60]}...")
        print(f"Profession: {prof!r}")
        print(f"  → Archetype : {result.archetype}")
        print(f"  → Score     : {result.score}")
        print(f"  → Signals   : {result.signals[:3]}")
        print()

    # Test validate_and_fix_profile with 'expert' experience
    print("=== validate_and_fix_profile ===")
    p = {"archetype": "THE CORNER OFFICE", "profession": "CEO",
         "experience": "expert", "profile_confidence": 0.95}
    fixed = validate_and_fix_profile(p)
    print(f"'expert' → '{fixed['experience']}' (expected 'advanced')")  # should print 'advanced'

    p2 = {"archetype": "THE CAREFUL PLANNER", "profession": "unknown",
          "experience": "intermediate", "profile_confidence": 0.45,
          "goal": "protect corpus"}
    fixed2 = validate_and_fix_profile(p2, conversation="I keep everything in FDs and PPF")
    print(f"'unknown' profession → re-classified as: {fixed2['archetype']}")
