import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from embed import get_embedding
from ingest import setup_collection, ingest_chunks
from retrieve import retrieve
from parse import parse_pdf
from chunk import chunk
from openai import OpenAI

from query_parser import parse_query

VALID_ZONES = {"A1", "A2", "RA", "RE40", "RE20", "RE15", "RE11", "RE9", "RS", "R1", "RU", "R2", "RD1.5", "RM1", "RMP", "CR", "C1", "C1.5", "C2", "C4", "C5", "CM", "MR1", "M1", "M2", "M3", "P", "PB", "OS", "GW", "PF"}

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

    # Create chunks from pdf 
    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    text = parse_pdf(pdf_path)
    chunks = chunk(text)


    # Create collection and ingest using chunks from pdf 
    collection_name = "eco_zoning"
    setup_collection(q_client, collection_name)
    ingest_chunks(q_client, collection_name, openai_client, chunks)

    # Prompt user for query and zone
    query = input("Enter a query: ").strip()
    if not query:
        print("Empty query provided. Exiting.")
        sys.exit(0)

    zone  = parse_query(query, openai_client).zone
    if zone is None:
        print("Could not identify a valid zone from your query. Please mention a zone code like R1, C2, or A1.")
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
        
