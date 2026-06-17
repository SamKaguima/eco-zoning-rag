from openai import OpenAI


def get_embedding(text: str, client: OpenAI) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    embedding = get_embedding("This is a test sentence.", client)
    print(len(embedding))
    print([round(x, 4) for x in embedding[:5]])
