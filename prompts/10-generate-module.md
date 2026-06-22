# Task: Generate module

Create `src/generate.py` with the following — no placeholders, fully implemented.

## Summary
This modules takes in user query and chuunks from retrive module and generates a response using LLM.

## Functions

`generate_response(query: str, chunks: list[dict], client: OpenAI) -> str`
- It takes a string query and a list of chunks and returns a string response.
- using the LLM, it will generate a response based on the query and the provided chunks.
- Use this system prompt: "You are an expert zoning consultant for Los Angeles. 
  Answer the user's question using ONLY the zoning regulations provided below. 
  If the answer cannot be found in the provided text, say 'I cannot find that 
  information in the available zoning documents.' Do not use any outside knowledge."
- Format the chunks into the user message by joining their text fields with 
  newlines and prepending "Relevant zoning regulations:\n" before the query.
- If chunks is an empty list, return "No relevant zoning information found for your query."

## Imports
Only these imports should be used:
- from openai import OpenAI
- from dotenv import load_dotenv
- import os 

## Main block
When run directly from project root (`python src/[filename].py`):
1. Load `.env` using python-dotenv
2. Instantiate clients using OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
3. from prototype import FAKE_CHUNKS
4. Use the first 3 chunks from FAKE_CHUNKS as the input chunks for testing.
5. Call generate_response with the following query "what is the max height for downtown buildings?" and the test chunks.
6. print the generated response to show the output from the LLM.

## What not to do
- Do not implement any retrieval logic in this module.
- Do not implement any logic related to parsing or extracting zone information.
- Do not use any imports other than the ones specified above.
- Do not use any other information apart from the query and the provided chunks to generate the response.
- Do not instantiate the OpenAI client inside generate_response — it must be injected as a parameter.
