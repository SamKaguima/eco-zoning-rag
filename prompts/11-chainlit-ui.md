# Task: Chainlit UI Module

- Create `src/app.py` with the following — no placeholders, fully implemented.
- Define COLLECTION_NAME = "eco_zoning" at module level.


## Summary
This module sets up a Chainlit UI for the zoning application. It provides an interface for users to input queries and receive zoning information.

## Event Handlers

### @cl.on_chat_start
- Load .env
- Instantiate QdrantClient(":memory:") and OpenAI client
- Parse the PDF at "data/raw/LA-zoning-regulations.pdf" using parse_pdf()
- Chunk the text using chunk()
- Call setup_collection() and ingest_chunks() to load chunks into Qdrant
- Send a welcome message: "Welcome to the LA Zoning Assistant! Ask me anything about LA zoning regulations."
- Store qdrant client, openai client, and collection name in cl.user_session

### @cl.on_message
- Retrieve qdrant client, openai client, and collection name from cl.user_session
- Send a thinking message: "Searching zoning documents..."
- Pass the user message to parse_query() to extract the zone
- If zone is None, reply "Could not identify a zone in your query. Please mention a zone code like R1, C2, or A1."
- Call retrieve() with the query and extracted zone
- Call generate_response() with the query and hits
- Send the generated response back to the user

## Imports
Only these imports should be used:
- import chainlit as cl
- from dotenv import load_dotenv
- import os 
- from openai import OpenAI
- from qdrant_client import QdrantClient
- from parse import parse_pdf 
- from query_parser import parse_query
- from retrieve import retrieve
- from generate import generate_response
- from chunk import chunk
- from ingest import ingest_chunks, setup_collection


## Running the app
- run with `chainlit run src/app.py` from the project root.


## What not to do
- Do not load the pdf on every request only load it once at the start of the app.
- Do not impliment any retrieval logic in this module.
- Do not implement any logic related to parsing or extracting zone information.
- Do not use any imports other than the ones specified above.
- Do not store clients as global variables — use cl.user_session exclusively.
- Do not re-parse or re-ingest the PDF on every message — only in on_chat_start.
- Do not define any helper functions — only call existing modules.