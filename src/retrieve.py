from qdrant_client import QdrantClient
from openai import OpenAI
from embed import get_embedding
from prototype import FAKE_CHUNKS
from ingest import ingest_chunks, setup_collection
import os


def retrieve(
    query: str,
    zone: str,
    qdrant: QdrantClient,
    openai: OpenAI,
    collection: str,
    top_k: int = 5
) -> list[dict]:
    """Retrieve and query data from a Qdrant collection.
    
    Embeds the query, filters by zone using payload, and returns top_k results.
    
    Args:
        query: The search query string
        zone: The zone to filter by (e.g., "downtown", "harbor")
        qdrant: QdrantClient instance
        openai: OpenAI client instance
        collection: Collection name
        top_k: Number of results to return
    
    Returns:
        A list of dicts with keys ('text', 'topic', 'score')
    """
    query_embedding = get_embedding(query, openai)
    
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    results = qdrant.query_points(
        collection_name=collection,
        query=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="zone", match=MatchValue(value=zone))]
        ),
        limit=top_k
    ).points
    
    output = []
    for result in results:
        output.append({
            "text": result.payload["text"],
            "topic": result.payload["topic"],
            "score": result.score
        })
    
    return output


if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # 1. Load .env
    load_dotenv()
    
    # 2. Instantiate clients
    qdrant = QdrantClient(":memory:")
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 3. Setup collection
    collection_name = "eco_zoning"
    setup_collection(qdrant, collection_name)
    
    # 4. Ingest fake chunks
    ingest_chunks(qdrant, collection_name, openai, FAKE_CHUNKS)
    
    # 5. First retrieve call (downtown zone)
    print("=== Query 1: downtown zone ===")
    query1 = "What height restrictions apply?"
    zone1 = "downtown"
    results1 = retrieve(query1, zone1, qdrant, openai, collection_name)
    for i, result in enumerate(results1, 1):
        print(f"\n{i}. Topic: {result['topic']} | Score: {result['score']:.4f}")
        print(f"   Text: {result['text']}")
    
    # 7. Second retrieve call (harbor zone)
    print("\n\n=== Query 2: harbor zone ===")
    query2 = "What height restrictions apply?"
    zone2 = "harbor"
    results2 = retrieve(query2, zone2, qdrant, openai, collection_name)
    for i, result in enumerate(results2, 1):
        print(f"\n{i}. Topic: {result['topic']} | Score: {result['score']:.4f}")
        print(f"   Text: {result['text']}")
