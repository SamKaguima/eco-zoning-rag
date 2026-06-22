import os
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import instructor

VALID_ZONES = {
    "A1", "A2", "RA", "RE40", "RE20", "RE15", "RE11", "RE9", "RS", "R1", 
    "RU", "R2", "RD1.5", "RM1", "RMP", "CR", "C1", "C1.5", "C2", "C4", 
    "C5", "CM", "MR1", "M1", "M2", "M3", "P", "PB", "OS", "GW", "PF"
}

class ZoneFilter(BaseModel):
    zone: str | None

def parse_query(query: str, client: OpenAI) -> ZoneFilter:
    if query is None:
        # Resolving conflict: "wait for response" vs "do not print inside parse_query".
        # We use input() to wait for the user, but we do not use print().
        query = input("Query is None. Please provide a valid query: ")

    instructor_client = instructor.from_openai(client)
    
    result = instructor_client.chat.completions.create(
        model="gpt-4o",
        response_model=ZoneFilter,
        messages=[
            {
                "role": "system",
                "content": f"Extract the zoning code from the user's query. Valid zones are: {', '.join(VALID_ZONES)}. If no valid zone is found, return None."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    
    if result.zone not in VALID_ZONES:
        result.zone = None
        
    return result

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    result = parse_query("what is the max height for R1 buildings?", client)
    print(result)
