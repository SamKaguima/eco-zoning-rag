from retrieve import retrieve
from ingest import setup_collection, ingest_chunks
from prototype import FAKE_CHUNKS
import pytest
from qdrant_client import QdrantClient

COLLECTION_NAME = "eco_zoning"


@pytest.fixture
def ingested_clients(fake_openai_client) -> tuple[QdrantClient, object]:
    qdrant = QdrantClient(":memory:")
    setup_collection(qdrant, COLLECTION_NAME)
    ingest_chunks(qdrant, COLLECTION_NAME, fake_openai_client, FAKE_CHUNKS)
    return qdrant, fake_openai_client


def test_retrieve_returns_only_results_from_requested_zone(ingested_clients: tuple[QdrantClient, object]) -> None:
    qdrant, openai = ingested_clients

    results = retrieve(
        "What height restrictions apply?",
        "downtown",
        qdrant,
        openai,
        COLLECTION_NAME,
    )

    assert results

    text_to_zone = {chunk["text"]: chunk["zone"] for chunk in FAKE_CHUNKS}
    for result in results:
        assert result["text"] in text_to_zone
        assert text_to_zone[result["text"]] == "downtown"


def test_retrieve_returns_empty_list_when_collection_has_no_chunks(fake_openai_client) -> None:
    qdrant = QdrantClient(":memory:")
    setup_collection(qdrant, COLLECTION_NAME)

    results = retrieve(
        "What height restrictions apply?",
        "downtown",
        qdrant,
        fake_openai_client,
        COLLECTION_NAME,
    )

    assert results == []
