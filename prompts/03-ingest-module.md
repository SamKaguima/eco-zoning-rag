# Task: Ingest module

Create 'src/ingest.py' with the following - no placeholders, fully implemented. 

## Functions

'setup_collection(client: QdrantClient, name: str) -> None:' 

- This should create a cosine collection with vector size 1536(matching text-embedding-3-small)
- This should create a keyword index on zone (will be filtered on every query)
- This should create a keyword index on topic
- If the collection already exists, skip creation and continue without raising an error.

'ingest_chunks(qdrant: QdrantClient, name: str, openai: OpenAI, chunks: list[dict]) -> int:'

- Should call embed module to embed the chunks and ingest them into the collection.
- Should return the number of chunks ingested.
- If any chunk is missing a required key (text, zone, topic, doc_type, source), raise a ValueError with a message identifying which key is missing.

## Imports 
'from qdrant_client import QdrantClient'
'from openai import OpenAI'
'from src.embed import get_embedding'
'import os'
only these imports should be used in the module.

## Main block
This should follow the following 6 steps:
1. load '.env' using python-dotenv
2. Instantiate QdrantClient(":memory:") for Qdrant and OpenAI(api_key=os.getenv("OPENAI_API_KEY")) for OpenAI.
3. call setup_collection() to ensure the collection is created.
4. use Fake Chunks from 'src/prototype.py' to test ingest_chunks().
5. print the number of chunks ingested.
6. Run a raw Qdrant scroll to print back what's actually stored in the collection.

## What not to do 
- This module does not read PDFs or text files.
- This module does not chunk texts.
- This module does not handle queries. 
- This module does not do batching or retry logic yet. 