# Task: Query Parser Module 

Create `src/query_parser.py` with the following — no placeholders, fully implemented.

## Summary
THis module takes in a user query and parses it into a structure object that returns the zone. 

## Module-level constants 
`VALID_ZONES as this list: VALID_ZONES = {"A1", "A2", "RA", "RE40", "RE20", "RE15", "RE11", "RE9", "RS", "R1", "RU", "R2", "RD1.5", "RM1", "RMP", "CR", "C1", "C1.5", "C2", "C4", "C5", "CM", "MR1", "M1", "M2", "M3", "P", "PB", "OS", "GW", "PF"}`

## Functions

`Class ZoneFilter(BaseModel)` 
- creates an object that has the following attributes: 
    - `zone: str` | `None`

`parse_query(query: str, client: OpenAI ) -> ZoneFilter`
- it takes a string query and returns a zonefilter object with the zone.
- this function will use LLM to arse the query and extract the zone information. 
- If the extracted zone is not in the list of valid zones, the function should return a zonefilter object with `zone` set to `None`. 
- If the query is None, print a message asking for clarification, and wait for response 

## Imports
Only these imports should be used:
- from pydantic import BaseModel
- from openai import OpenAI
- from dotenv import load_dotenv
- import instructor
- import os

## Main block
When run directly from project root (`python src/query_parser.py`):
1. Load `.env` using python-dotenv
2. Instantiate openai client using OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
3. Call parse query with the following query "what is the max height for R1 buildings?" 
4. print the returned ZoneFilter object to show the extracted zone. 

## What not to do
- Do not implement any retrieval logic in this module.
- Do not implement any logic related to embedding or interacting with Qdrant.
- Do not use any imports other than the ones specified above.
- Do not import from main.py — it will trigger the entire pipeline on import.
- Do not define VALID_ZONES inside the function — define it at module level so it is reusable.
- Do not return a raw string — always return a ZoneFilter object.
- Do not skip validation — always check the extracted zone against VALID_ZONES before returning.
- Do not instantiate the OpenAI client inside parse_query — it must be injected as a parameter.
- Do not print anything inside parse_query — printing only happens in the main block.