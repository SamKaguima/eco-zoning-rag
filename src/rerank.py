from dotenv import load_dotenv
import os
import cohere


def rerank(query: str, chunks: list[dict], co: cohere.Client, top_n: int = 5) -> list[dict]:
    if not chunks:
        return chunks

    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[chunk["text"] for chunk in chunks],
        top_n=top_n,
    )

    if not response.results:
        return chunks

    return [
        {**chunks[result.index], "relevance_score": result.relevance_score}
        for result in response.results
    ]


if __name__ == "__main__":
    load_dotenv()

    co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

    from prototype import FAKE_CHUNKS

    query = "What is the maximum buiding height in downtown zone ?"

    results = rerank(query, FAKE_CHUNKS, co)

    for i, result in enumerate(results, 1):
        print(f"{i}. score={result['relevance_score']:.4f} | {result['text']}")
