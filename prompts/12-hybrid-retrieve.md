# Task: Hybrid Retrieval Module

Create `src/hybrid_retrieve.py` with the following — no placeholders, fully implemented.

## Summary
This module implements a hyrid retrieval system that combines vector based retrieval using Qdrant and using indexes from a BM25 search. It is designed to retrieve relevant documents based on a query by leveraging both semantic similarity and keyword matching.

## Functions

`bm25_search(zone: str, query: str, bm25_index: BM25Okapi, chunks: list[dict] ) -> list[dict]`
- Takes in a zone, a query string, a BM25 index, and a list of document chunks. It performs a BM25 keyword search on the provided index and returns a list of dictionaries containing the top results.
- Filter the chunks to only the requested zone
- Tokenize the query into words 
- score each filtered chinks against the tokenized query using the BM25 index
- return the top results as a list of dicts matching this schema: 
    - ('text', 'topic', and 'score') for the top_k results
- if no results are found, return empty list.

`fuse_results(results1: list[dict], results2: list[dict]) -> list[dict]`
- takes to lists of dictionaries containing search results from vecor search and BM25 search, and combines them using Reciprical Rank Fusion (RRF) to produce a final ranked list of results.
- For each unique chunk across both lists calculate:
  score = 1/(rank_in_vector_results + 60) + 1/(rank_in_bm25_results + 60)
- If a chunk only appears in one list, use len(list) + 1 as its rank in the other
- Return chunks sorted by fused score descending
 
`hybrid_retrieve(query: str, zone: str, qdrant: QdrantClient, openai: OpenAI, collection: str, bm25_index: BM25Okapi, chunks: list[dict], top_k: int = 20) -> list[dict]`
- Takes in the input above and calls bm25_search and retrieve functions to get both results then returns two lists of dictionaries containing the top results from both searches.
- Call `bm25_search(zone, query, bm25_index, chunks)` to get BM25 results.
- Call `retrieve(query, zone, qdrant, openai, collection, top_k)` to get vector search results.
- Call `fuse_results(vector_results, bm25_results)` to combine the results.
- Returns the top_k results from the fused list as a single list[dict]

## Imports
Only these imports should be used:
from rank_bm25 import BM25Okapi
from retrieve import retrieve
from openai import OpenAI
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv


## Main block
When run directly from project root (`python src/hybrid_retrieve.py`):
0. Import the following :
    - from prototype import FAKE_CHUNKS
    - from ingest import ingest_chunks, setup_collection
1. Load `.env` using python-dotenv
2. Instantiate clients using OpenAI(api_key=os.getenv("OPENAI_API_KEY")) and QdrantClient(":memory:") for Qdrant.
3. Build a BM25 index by tokenizing each chunk's text field using str.split() and passing the list of tokenized texts to BM25Okapi()
4. ingest FAKE_CHUNKS into Qdrant using the ingest module.
5. Call `hybrid_retrieve()` with a sample query found below.
    - sample query: "What is the maximum building height in zone R1?"
6. print the top 5 results from the hybrid retrieval.

## What not to do
- Do not instantiate OpenAI or QdrantClient inside any function — inject them as parameters.
- Do not return None from any function — always return an empty list if no results found.
- Do not re-implement vector search logic — call retrieve() from retrieve.py.
- Do not build the BM25 index inside hybrid_retrieve() — it must be passed in as a parameter.
- Do not import FAKE_CHUNKS or ingest at module level — only import them inside the __main__ block.
- Do not print anything inside any function — printing only happens in the main block.
- Do not modify the chunks list in place — always return new lists.