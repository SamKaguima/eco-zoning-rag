# # Task: Wire hybrid retrieval into pipeline

Update `src/app.py` and `src/main.py` — no placeholders, fully implemented.

## Summary

Wire rerank into `main.py` and `app.py` to use rerank module after hybrid_retrieval and before gerneration of the response inorder to rerank chunks to precision. 

## Changes

### src/app.py - on_message
- After the hybrid_retrieve() call, pass the hits and query to rerank()
- Call rerank(query, hits, co, top_n=5) where co is a cohere.ClientV2 instance
- Pass the reranked results to generate_response() instead of the raw hits
- Instantiate co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY")) in on_chat_start and store in cl.user_session under key "cohere_client"
- Retrieve co from cl.user_session in on_message before calling rerank

### src/main.py
- After the hybrid_retrieve() call, pass the hits and query to rerank()
- Call rerank(query, hits, co, top_n=5) where co is a cohere.ClientV2 instance
- Pass the reranked results to generate_response() instead of the raw hits
- Instantiate co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY")) after the OpenAI client

## Imports to add

### src/app.py
- import cohere
- from rerank import rerank

### src/main.py
- import cohere
- from rerank import rerank 

## What not to do
- Do not remove any existing imports that are still needed
- Do not instantiate the Cohere client inside any function
- Do not call rerank before hybrid_retrieve — order must be hybrid_retrieve → rerank → generate
- Do not pass more than top_n=5 results to generate_response