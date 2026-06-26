# # Task: Wire hybrid retrieval into pipeline

Update `src/app.py` and `src/main.py` — no placeholders, fully implemented.

## Summary

Rewire the `app.py` and `main.py` to use hybrid_retrieval module instead of the outdated retrieve. 

## Changes

### src/app.py — on_chat_start
- Build BM25 index by tokenizing each chunk's text field using str.split() 
  and passing the list of tokenized texts to BM25Okapi()
- Store the index and chunks list in cl.user_session under keys 
  "bm25_index" and "chunks"

### src/app.py — on_message
- Call hybrid_retrieve(query, zone, qdrant, openai, collection, bm25_index, chunks, top_k=20)
- Retrieve bm25_index and chunks from cl.user_session before calling

### src/main.py
- Build BM25 index by tokenizing each chunk's text field using str.split() 
  and passing the list of tokenized texts to BM25Okapi()
- Call hybrid_retrieve(query, zone, q_client, openai_client, collection_name, bm25_index, chunks, top_k=20)
- Remove the old retrieve() call entirely

## Imports to add

### src/app.py
- from rank_bm25 import BM25Okapi
- from hybrid_retrieve import hybrid_retrieve

### src/main.py
- from rank_bm25 import BM25Okapi
- from hybrid_retrieve import hybrid_retrieve

## What not to do
- Do not remove any existing imports that are still needed
- Remove the old retrieve() call entirely and replace with hybrid_retrieve()
- Do not rebuild the BM25 index on every message — only build it in on_chat_start