# Task: Rerank Module 

Create `src/rerank.py` with the following — no placeholders, fully implemented.

## Summary
This module serves as a layer ontop of the hybrid search module. It takes in the already searched chunks and reranks them with more precision returning a shorter list of chunks that are more precise. 

## Functions

`rerank(query: str, chunks: list[dict], co: cohere.Client, top_n: int = 5) -> list[dict]`
- This function takes in some chunks and outputs a reranked output of the chunk. 
- use rerank-english-v3.0 to rerank the chunks gotten from hybrid retrieve 
- return the top_n chunks
- If the returned results list is empty, return the original chunks unchanged as a fallback 
- if less results than top_k then return those results

## Imports
Only these imports should be used:
- from dotenv import load_dotenv 
- import os 
- import cohere 

## Main block
When run directly from project root (`python src/[filename].py`):
1. Load `.env` using python-dotenv
2. Instantiate clients using environment variables
    - co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
3. from prototype import FAKE_CHUNKS
4. call rerank with inputs  FAKE_CHUNKS, cohere_client and query What is the maximum buiding height in downtown zone ?
5. print each reranked chunk showing its text and relevance score

## What not to do
- Do Not use any other imports other than those specified in this file
- Do not re-implement any retrieval or search logic — only rerank what is passed in
- Do not instantiate the Cohere client inside rerank() — inject it as a parameter
- Do not print anything inside rerank() — only in the main block
- Do not return more chunks than top_n