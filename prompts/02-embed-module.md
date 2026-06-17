# Task: embed module

Create `src/embed.py` with the following — no placeholders, fully implemented.

## Function
`get_embedding(text: str, client: OpenAI) -> list[float]`

- Uses model `text-embedding-3-small`
- Client is passed in as a parameter, never instantiated inside the function
- Returns a plain list of floats
- No error handling, no retries, no caching — keep it minimal

## Imports
`from openai import OpenAI` only. No other dependencies.

## __main__ block
When run directly:
1. Load `.env` with python-dotenv
2. Instantiate OpenAI client from env
3. Call get_embedding("This is a test sentence.")
4. Print the vector length (should be 1536)
5. Print the first 5 dimensions rounded to 4 decimal places

## What not to do
- Do not batch inputs
- Do not add a cache layer
- Do not wrap in try/except
- Do not instantiate the OpenAI client inside get_embedding