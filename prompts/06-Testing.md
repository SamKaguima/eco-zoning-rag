# Task: Tests

Create `tests/test_retrieve.py` with the following — no placeholders, fully implemented.

## Summary
This module is responsible for testing the retrieve functionality. It should ensure that retieve returns valid result and zone 

## Tests 
Test 1: Assert that every result returned has zone equal to the requested zone

Test 2: When a query has no chunks, an empty list is returned not an error. 


## Imports
Only these imports should be used:
- 'from embed import get_embedding'
- 'from retrieve import retrieve'
- 'from ingest import setup_collection, ingest_chunks' 
- 'from prototype import FAKE_CHUNKS'
- 'import pytest'
- 'from qdrant_client import QdrantClient'
- 'from openai import OpenAI'


## What not to do
- Do not test implementation details of embed or ingest-only retrieve
- Do not mock the OpenAI API — use real embeddings via the API key from .env
- Do not connect to a real Qdrant server — use QdrantClient(":memory:") only

## Note 
Use a pytest fixture that sets up an in-memory QdrantClient, ingests FAKE_CHUNKS, and returns the clients. Load the OpenAI API key from .env for embeddings.