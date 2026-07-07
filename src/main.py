import os
import sys
import cohere
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from rank_bm25 import BM25Okapi
from embed import get_embedding
from ingest import setup_collection, ingest_chunks
from hybrid_retrieve import hybrid_retrieve
from rerank import rerank
from parse import parse_pdf
from chunk import chunk
from openai import OpenAI

from query_parser import parse_query
from generate import generate_response


VALID_ZONES = {"A1", "A2", "RA", "RE40", "RE20", "RE15", "RE11", "RE9", "RS", "R1", "RU", "R2", "RD1.5", "RM1", "RMP", "CR", "C1", "C1.5", "C2", "C4", "C5", "CM", "MR1", "M1", "M2", "M3", "P", "PB", "OS", "GW", "PF"}

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=api_key)
    cohere_client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
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

    bm25_index = BM25Okapi([c["text"].split() for c in chunks])

    # Prompt user for query and zone
    query = input("Enter a query: ").strip()
    if not query:
        print("Empty query provided. Exiting.")
        sys.exit(0)

    zone  = parse_query(query, openai_client).zone
    if zone is None:
        print("Could not identify a valid zone from your query. Please mention a zone code like R1, C2, or A1.")
        sys.exit(0)


    hits = hybrid_retrieve(query, zone, q_client, openai_client, collection_name, bm25_index, chunks, top_k=20)

    # Display results (tolerant to multiple hit formats)
    if not hits:
        print("No results returned.")
        sys.exit(0)
    


    reranked_hits = rerank(query, hits, cohere_client, top_n=5)

    response = generate_response(query, reranked_hits, openai_client)
    print("Response:\n", response)
