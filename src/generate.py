from openai import OpenAI
from dotenv import load_dotenv
import os


def generate_response(query: str, chunks: list[dict], client: OpenAI) -> str:
    if not chunks:
        return "No relevant zoning information found for your query."

    regulations = "\n".join(chunk["text"] for chunk in chunks)
    user_message = "Relevant zoning regulations:\n" + regulations + "\n\nQuery: " + query
    system_prompt = (
        "You are an expert zoning consultant for Los Angeles. "
        "Answer the user's question using ONLY the zoning regulations provided below. "
        "The regulations may be extracted from tables and appear fragmented — interpret them carefully. "
        "For height questions, look for values like '28 ft', '33 ft', or 'Roof ≥25%' patterns. "
        "If the answer cannot be found in the provided text, say 'I cannot find that "
        "information in the available zoning documents.' Do not use any outside knowledge."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    return response.choices[0].message.content or ""


if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    from prototype import FAKE_CHUNKS

    test_chunks = FAKE_CHUNKS[:3]
    query = "what is the max height for downtown buildings?"
    print(generate_response(query, test_chunks, client))
