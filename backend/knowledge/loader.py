# knowledge/loader.py
import json
import chromadb
from chromadb.utils import embedding_functions
import os

CHROMA_PATH = "./chroma_db"

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

def load_knowledge_base():
    """Load all ET products, events, and services into ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = get_embedding_function()

    # Create or get collection
    collection = client.get_or_create_collection(
        name="et_knowledge",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # Check if already loaded
    if collection.count() > 0:
        print(f"✅ Knowledge base already loaded ({collection.count()} items)")
        return collection

    documents = []
    metadatas = []
    ids = []

    # Load products
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "et_products.json")) as f:
        products = json.load(f)["products"]
    for p in products:
        text = f"{p['name']}: {p['description']} Features: {', '.join(p['key_features'])}. Ideal for: {', '.join(p['ideal_interests'])}."
        documents.append(text)
        metadatas.append({
            "type": "product",
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "price": p["price"],
            "cta": p["cta"],
            "url": p["url"],
            "archetypes": ",".join(p["ideal_archetypes"]),
        })
        ids.append(f"product_{p['id']}")

    # Load events
    with open(os.path.join(base_dir, "et_events.json")) as f:
        events = json.load(f)["events"]
    for e in events:
        text = f"{e['name']}: {e['description']}"
        documents.append(text)
        metadatas.append({
            "type": "event",
            "id": e["id"],
            "name": e["name"],
            "category": "events",
            "price": e.get("price", ""),
            "cta": "Register now",
            "url": e.get("url", ""),
            "archetypes": ",".join(e.get("ideal_archetypes", [])),
        })
        ids.append(f"event_{e['id']}")

    # Load services
    with open(os.path.join(base_dir, "et_services.json")) as f:
        services = json.load(f)["services"]
    for s in services:
        text = f"{s['name']}: {s['description']}. Ideal for: {', '.join(s.get('ideal_interests', []))}."
        documents.append(text)
        metadatas.append({
            "type": "service",
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "price": "Free",
            "cta": s.get("cta", "Learn more"),
            "url": s.get("url", ""),
            "archetypes": ",".join(s.get("ideal_archetypes", [])),
        })
        ids.append(f"service_{s['id']}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Loaded {len(documents)} items into ChromaDB")
    return collection


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = get_embedding_function()
    return client.get_or_create_collection(name="et_knowledge", embedding_function=ef)
