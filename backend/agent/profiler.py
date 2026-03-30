# agent/profiler.py
"""
Profile extraction utilities for ET Artha.
Handles parsing and validating the extracted user profile.
"""

VALID_ARCHETYPES = [
    "THE MARKET MAVERICK",
    "THE WEALTH BUILDER",
    "THE CORNER OFFICE",
    "THE STARTUP SHERPA",
    "THE CAREFUL PLANNER",
    "THE CURIOUS LEARNER",
]

VALID_EXPERIENCE_LEVELS = ["beginner", "intermediate", "expert"]


def validate_profile(profile: dict) -> dict:
    """Validate and sanitize extracted profile to ensure required fields exist."""
    if not profile:
        return get_default_profile()

    archetype = profile.get("archetype", "")
    if archetype not in VALID_ARCHETYPES:
        profile["archetype"] = "THE CURIOUS LEARNER"

    experience = profile.get("experience", "")
    if experience not in VALID_EXPERIENCE_LEVELS:
        profile["experience"] = "beginner"

    if not isinstance(profile.get("interests"), list):
        profile["interests"] = []

    if "profile_confidence" not in profile:
        profile["profile_confidence"] = 0.5

    return profile


def get_default_profile() -> dict:
    """Return a safe default profile when extraction fails."""
    return {
        "archetype": "THE CURIOUS LEARNER",
        "profession": "unknown",
        "experience": "beginner",
        "goal": "learn about investing",
        "interests": [],
        "profile_confidence": 0.3,
    }


def profile_is_complete(profile: dict) -> bool:
    """Check if we have enough information to make good recommendations."""
    if not profile:
        return False
    confidence = profile.get("profile_confidence", 0)
    has_archetype = profile.get("archetype") in VALID_ARCHETYPES
    has_interests = len(profile.get("interests", [])) > 0
    return confidence >= 0.6 and has_archetype and has_interests
