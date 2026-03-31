# knowledge/retriever.py
from knowledge.loader import get_collection

def retrieve_for_profile(profile: dict, n_results: int = 6) -> list[dict]:
    """
    Given a user profile, retrieve the most relevant ET products.
    Uses semantic search on interests + archetype.
    """
    collection = get_collection()

    # Build search query from profile
    query_parts = []
    if profile.get("archetype"):
        query_parts.append(profile["archetype"].replace("THE ", ""))
    if profile.get("interests"):
        query_parts.extend(profile["interests"])
    if profile.get("goal"):
        query_parts.append(profile["goal"])
    if profile.get("profession"):
        query_parts.append(profile["profession"])

    query = " ".join(query_parts)

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    items = []
    for i, meta in enumerate(results["metadatas"][0]):
        items.append({
            "name": meta["name"],
            "category": meta["category"],
            "price": meta.get("price", ""),
            "cta": meta.get("cta", ""),
            "url": meta.get("url", ""),
            "relevance_score": 1 - results["distances"][0][i],
            "document": results["documents"][0][i],
        })

    return items


def format_products_for_prompt(products: list[dict]) -> str:
    """Format retrieved products as text for the recommendation prompt."""
    lines = []
    for p in products:
        lines.append(f"- {p['name']} ({p['category']}): {p['document'][:200]}... Price: {p['price']}. CTA: {p['cta']}. URL: {p['url']}")
    return "\n".join(lines)
