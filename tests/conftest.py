import hashlib
import random
from types import SimpleNamespace

import pytest

EMBEDDING_DIM = 1536


def _deterministic_vector(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """Same text always maps to the same vector, without calling any API."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return [rng.uniform(-1, 1) for _ in range(dim)]


class FakeEmbeddings:
    def create(self, input: str, model: str) -> SimpleNamespace:
        return SimpleNamespace(data=[SimpleNamespace(embedding=_deterministic_vector(input))])


class FakeOpenAIClient:
    """Duck-types the subset of the OpenAI client this project calls
    (client.embeddings.create), so tests never hit the network or need
    OPENAI_API_KEY."""

    def __init__(self) -> None:
        self.embeddings = FakeEmbeddings()


@pytest.fixture
def fake_openai_client() -> FakeOpenAIClient:
    return FakeOpenAIClient()
