import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from embed import get_embedding
from ingest import setup_collection, ingest_chunks
from retrieve import retrieve
from prototype import FAKE_CHUNKS
from openai import OpenAI

VALID_ZONES = {"downtown", "harbor", "midtown"}

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=api_key)
    if not api_key:
        print("OPENAI_API_KEY not set in environment. Please add it to .env")
        sys.exit(1)

    # Ensure downstream helpers that read env can access the key
    os.environ["OPENAI_API_KEY"] = api_key

    # Initialize an in-memory Qdrant client if possible; fall back gracefully
    q_client = QdrantClient(":memory:")

    # Create collection and ingest provided fake chunks (in-memory usage)
    collection_name = "eco_zoning"
    setup_collection(q_client, collection_name)
    ingest_chunks(q_client, collection_name, openai_client, FAKE_CHUNKS)

    # Prompt user for query and zone
    zone = input("Zone (downtown/harbor/midtown): ").strip().lower()
    if zone not in VALID_ZONES:
        print(f"Invalid zone: {zone}. Must be one of {', '.join(VALID_ZONES)}")
        sys.exit(1)

    query = input("Enter a query: ").strip()
    if not query:
        print("Empty query provided. Exiting.")
        sys.exit(0)

    # Call retrieve — try common argument orders to be tolerant to implementation
    hits = retrieve (query, zone, q_client, openai_client, collection_name)


    # Display results (tolerant to multiple hit formats)
    if not hits:
        print("No results returned.")
        sys.exit(0)

    print("\nResults:\n")
    for i, h in enumerate(hits, start=1):
        print(f"{i}. Topic: {h['topic']} | Score: {h['score']: .4f}")
        print(f" Text: {h['text']}\n")
        
