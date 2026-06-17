# Task: Main 

Create `src/main.py` with the following — no placeholders, fully implemented.

## Summary
This module wires everything together. It will run the full pipeling from 'embed.py', 'ingest.py', 'retrieve.py', and  use dummy data from 'prototype.py' this will be the full end-to-end pipeline. It will also include a main block that will run the full pipeline when executed directly.


## Imports
Only these imports should be used:
- 'import os'
- 'from embed import get_embedding'
- 'from ingest import setup_collection, ingest_chunks'
- 'from retrieve import retrieve'
- 'from prototype import FAKE_CHUNKS'
- 'from qdrant_client import QdrantClient'



## Main block
When run directly from project root (`python src/main.py`):
1. Load `.env` using python-dotenv
2. Instantiate QdrantClient(":memory") and OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
3. create a collection using setup_collection()
4. ingest FAKE_CHUNKS into the collection using ingest_chunks()
5. ask for an input query and zone from the user, Print an error and exit if zone is not one of: downtown, harbor, or midtown. 
6. Call retrieve() with the user input query and zone 
7. print the results in a readable format showing text, topic, and score for each hit
## What not to do
- This module does not read PDFs or text files.
- This module does not chunk texts.
- This module does not handle queries beyond the retrieve() function.
- this module should not write to Qdrant
- Do not write any logic that already exists in embed.py, ingest.py, or retrieve.py - call those functions, do not re-implement them here.
- Do not define any new functions - this is a scripts not a module with reusable functions.