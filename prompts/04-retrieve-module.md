# Task: Retrieve module

Create `src/retrieve.py` with the following — no placeholders, fully implemented.

## Summary
Module to retrieve and query data from a Qdrant collection. It will handle filtering based on zone, and return a list of dicts with keys ('text', 'topic', and 'score').


## Functions
'retrieve(query: str, zone: str, qdrant: QdrantClient, openai: OpenAI, collection: str, top_k: int = 5) -> list[dict]:'
 
 - This should embed a query 
 - This shoud filter by zone payload
 - This should return a list of dicts with keys ('text', 'topic', and 'score') for the top_k results

## Imports
Only these imports should be used:
- 'from qdrant_client import QdrantClient'
- 'from openai import OpenAI'
- 'from src.embed import get_embedding'
- 'from src.prototype import FAKE_CHUNKS'
- 'from src.ingest import ingest_chunks, setup_collection'
- 'import os'

## Main block
When run directly from project root (`python src/retrieve.py`):
1. Load `.env` using python-dotenv
2. Instantiate clients using QdrantClient(":memory") and OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
3. Call setup_collection() to create the collection
4. Call ingest_chunks() to load FAKE_CHUNKS into the collection
5. Call retrieve() with query "What height restrictions apply?" and zone "downtown"
6. Print the results in a readable format showing text, topic, and score for each hit
7. Run a a secont retrieve() with query "What height restrictions apply?" and zone "harbor" to demonstrate filtering
8. Print the results in a readable format showing text, topic, and score for each hit

## What not to do
- This module does not read PDFs or text files.
- This module does not chunk texts.
- This module does not handle queries beyond the retrieve() function.
- This module should not write to Qdrant 
- This module does not do batching or retry logic yet.
