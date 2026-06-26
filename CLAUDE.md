# Eco-Zoning RAG — Claude Code Instructions

## Project summary
A retrieval-augmented generation system that answers zoning and climate
questions for specific city neighborhoods. Currently uses LA zoning regulations
as the data source. Users query in natural language; the system extracts the
zone, retrieves relevant chunks, and generates a grounded answer.

## Stack
- Python 3.11
- qdrant-client (in-memory for dev)
- openai (embeddings: text-embedding-3-small, generation: gpt-4o)
- rank-bm25 (keyword search)
- instructor (structured output for query parsing)
- chainlit (chat UI)
- python-dotenv
- pytest

## Project structure
eco-zoning-rag/
├── src/
│   ├── embed.py           # get_embedding() — text to vector
│   ├── ingest.py          # setup_collection(), ingest_chunks()
│   ├── parse.py           # parse_pdf() — PDF to clean text
│   ├── chunk.py           # chunk() — text to list of dicts with metadata
│   ├── retrieve.py        # retrieve() — zone-filtered vector search
│   ├── hybrid_retrieve.py # hybrid_retrieve() — BM25 + vector + RRF fusion
│   ├── query_parser.py    # parse_query() — extract zone from natural language
│   ├── generate.py        # generate_response() — LLM synthesis from chunks
│   ├── prototype.py       # FAKE_CHUNKS — test data for 3 fake zones
│   ├── app.py             # Chainlit UI
│   └── main.py            # CLI entrypoint
├── data/
│   ├── raw/               # source PDFs (gitignored)
│   └── chunks/            # processed chunk JSON files
├── prompts/               # numbered task cards for agent-driven development
├── tests/
│   └── test_retrieve.py
├── .env                   # OPENAI_API_KEY (gitignored)
└── conftest.py            # adds src/ to pytest path

## Coding conventions
- All clients (OpenAI, QdrantClient) injected as parameters — never instantiated inside functions
- Explicit type hints on all parameters and return values
- No global state outside main.py and app.py
- Each module has a runnable __main__ block for manual testing
- Run scripts from project root: python src/module.py
- Relative imports without src. prefix (e.g. from embed import get_embedding)

## Metadata schema
Every chunk carries this payload in Qdrant:
{
  "text":     string,   # chunk content
  "zone":     string,   # e.g. "R1", "C2", "A1"
  "topic":    string,   # e.g. "zoning_regulations"
  "doc_type": string,   # "ordinance" | "climate_study" | "gis_data"
  "source":   string    # original filename
}
zone and topic are indexed as keyword payload fields.

## Running the project
- Chainlit UI: chainlit run src/app.py --port 8080
- CLI: python src/main.py
- Tests: pytest tests/ -v
- Any module standalone: python src/module.py (from project root)

## Current data source
LA Zoning Regulations — data/raw/LA-zoning-regulations.pdf
17 pages, 68 chunks, zones like R1, C2, A1, RE40 etc.

## Known issues
- Qdrant payload indexes have no effect in memory mode — expected warning, ignore it
- Chunk zone tagging uses regex — occasionally misidentifies zone for overlap chunks
- top_k=20 needed for reliable retrieval of height-related R1 chunks

## What not to do
- Do not use langchain or llamaindex unless explicitly asked
- Do not instantiate clients inside functions
- Do not use global variables outside main.py and app.py
- Do not add dependencies not in requirements.txt without flagging it
- Do not write placeholder comments — implement fully
- Do not use src. prefix in imports