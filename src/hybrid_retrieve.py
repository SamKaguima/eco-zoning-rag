from rank_bm25 import BM25Okapi
from retrieve import retrieve
from openai import OpenAI
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv


def bm25_search(zone: str, query: str, bm25_index: BM25Okapi, chunks: list[dict]) -> list[dict]:
    zone_chunks = [c for c in chunks if c.get("zone") == zone]
    if not zone_chunks:
        return []

    tokenized_query = query.split()
    zone_indices = [i for i, c in enumerate(chunks) if c.get("zone") == zone]
    zone_corpus = [chunks[i]["text"].split() for i in zone_indices]

    local_index = BM25Okapi(zone_corpus)
    scores = local_index.get_scores(tokenized_query)

    ranked = sorted(
        zip(zone_chunks, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return [
        {"text": chunk["text"], "topic": chunk.get("topic", ""), "score": float(score)}
        for chunk, score in ranked
        if score > 0
    ]


def fuse_results(results1: list[dict], results2: list[dict]) -> list[dict]:
    texts1 = {r["text"]: rank for rank, r in enumerate(results1)}
    texts2 = {r["text"]: rank for rank, r in enumerate(results2)}

    all_texts = set(texts1) | set(texts2)
    fused = {}

    for text in all_texts:
        rank1 = texts1.get(text, len(results1))
        rank2 = texts2.get(text, len(results2))
        score = 1 / (rank1 + 60) + 1 / (rank2 + 60)

        chunk = next(
            (r for r in results1 + results2 if r["text"] == text),
            {"text": text, "topic": ""},
        )
        fused[text] = {"text": chunk["text"], "topic": chunk.get("topic", ""), "score": score}

    return sorted(fused.values(), key=lambda x: x["score"], reverse=True)


def hybrid_retrieve(
    query: str,
    zone: str,
    qdrant: QdrantClient,
    openai: OpenAI,
    collection: str,
    bm25_index: BM25Okapi,
    chunks: list[dict],
    top_k: int = 20,
) -> list[dict]:
    bm25_results = bm25_search(zone, query, bm25_index, chunks)
    vector_results = retrieve(query, zone, qdrant, openai, collection, top_k)
    fused = fuse_results(vector_results, bm25_results)
    return fused[:top_k]


if __name__ == "__main__":
    from prototype import FAKE_CHUNKS
    from ingest import ingest_chunks, setup_collection

    load_dotenv()

    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    qdrant = QdrantClient(":memory:")

    tokenized_corpus = [chunk["text"].split() for chunk in FAKE_CHUNKS]
    bm25_index = BM25Okapi(tokenized_corpus)

    collection_name = "eco_zoning"
    setup_collection(qdrant, collection_name)
    ingest_chunks(qdrant, collection_name, openai, FAKE_CHUNKS)

    query = "What is the maximum building height in zone R1?"
    zone = "downtown"

    results = hybrid_retrieve(query, zone, qdrant, openai, collection_name, bm25_index, FAKE_CHUNKS)

    for i, result in enumerate(results[:5], 1):
        print(f"{i}. [{result['topic']}] score={result['score']:.6f} | {result['text']}")
