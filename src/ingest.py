from qdrant_client import QdrantClient
from openai import OpenAI
from embed import get_embedding
import os


def setup_collection(client: QdrantClient, name: str) -> None:
    """Create a Qdrant collection with vector size 1536 and keyword indices on zone and topic.
    
    If the collection already exists, skip creation without raising an error.
    """
    from qdrant_client.models import VectorParams, Distance
    
    try:
        client.get_collection(name)
    except Exception:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        client.create_payload_index(
            collection_name=name,
            field_name="zone",
            field_schema="keyword",
        )
        client.create_payload_index(
            collection_name=name,
            field_name="topic",
            field_schema="keyword",
        )


def ingest_chunks(qdrant: QdrantClient, name: str, openai: OpenAI, chunks: list[dict]) -> int:
    """Embed chunks and ingest them into the Qdrant collection.
    
    Validates that each chunk has required keys: text, zone, topic, doc_type, source.
    Returns the number of chunks ingested.
    Raises ValueError if any required key is missing.
    """
    required_keys = {"text", "zone", "topic", "doc_type", "source"}
    
    for i, chunk in enumerate(chunks):
        missing_keys = required_keys - set(chunk.keys())
        if missing_keys:
            raise ValueError(f"Chunk {i} is missing required key(s): {', '.join(sorted(missing_keys))}")
    
    vectors = []
    for chunk in chunks:
        embedding = get_embedding(chunk["text"], openai)
        vectors.append(embedding)
    
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=i,
            vector=vector,
            payload={
                "text": chunk["text"],
                "zone": chunk["zone"],
                "topic": chunk["topic"],
                "doc_type": chunk["doc_type"],
                "source": chunk["source"],
            }
        )
        points.append(point)
    
    qdrant.upsert(
        collection_name=name,
        points=points,
    )
    
    return len(chunks)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from prototype import FAKE_CHUNKS
    
    # 1. Load .env
    load_dotenv()
    
    # 2. Instantiate clients
    qdrant = QdrantClient(":memory:")
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 3. Setup collection
    collection_name = "eco_zoning"
    setup_collection(qdrant, collection_name)
    
    # 4. Ingest fake chunks
    num_ingested = ingest_chunks(qdrant, collection_name, openai, FAKE_CHUNKS)
    
    # 5. Print number of chunks ingested
    print(f"Ingested {num_ingested} chunks")
    
    # 6. Scroll collection to see what's stored
    points, _ = qdrant.scroll(collection_name=collection_name, limit=100)
    print(f"\nStored points ({len(points)} total):")
    for point in points:
        print(f"  ID: {point.id}, Zone: {point.payload['zone']}, Topic: {point.payload['topic']}, Text: {point.payload['text'][:60]}...")
