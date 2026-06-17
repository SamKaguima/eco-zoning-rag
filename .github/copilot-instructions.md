# Eco-Zoning RAG — Copilot instructions

## Project summary
A retrieval-augmented generation system that answers zoning and climate
questions for specific city neighborhoods. Users query by zone; the system
returns grounded answers from official ordinances and climate data.

## Stack
- Python 3.11
- qdrant-client (in-memory for dev, server for prod)
- openai (embeddings: text-embedding-3-small, generation: gpt-4o)
- python-dotenv
- pytest for tests
- chainlit for UI (added later)

## Project structure
eco-zoning-rag/
├── src/
│   ├── embed.py       # embedding helpers
│   ├── ingest.py      # collection setup + chunk ingestion
│   ├── retrieve.py    # filtered vector search
│   └── main.py        # pipeline entrypoint
├── data/
│   ├── raw/           # source PDFs and CSVs (gitignored)
│   └── chunks/        # processed chunk JSON files
├── tests/
└── .env               # OPENAI_API_KEY (gitignored)

## Coding conventions
- All clients (OpenAI, QdrantClient) are injected as function parameters — never
  instantiated inside functions. This keeps everything testable.
- Functions have explicit type hints on all parameters and return values.
- No global state outside of main.py.
- Each module has a runnable __main__ block for quick manual testing.
- Chunk dicts always have these keys: text, zone, topic, doc_type, source.

## Metadata schema
Every ingested chunk carries this payload in Qdrant:
{
  "text":     string,   # the chunk content
  "zone":     string,   # e.g. "downtown", "harbor", "midtown"
  "topic":    string,   # e.g. "height", "setback", "wind", "environment"
  "doc_type": string,   # "ordinance" | "climate_study" | "gis_data"
  "source":   string    # original filename
}
zone and topic are indexed as keyword payload fields.

## What not to do
- Do not use langchain or llamaindex unless explicitly asked.
- Do not instantiate clients inside functions.
- Do not use global variables.
- Do not add dependencies not in requirements.txt without flagging it.
- Do not write placeholder comments like "# add logic here" — implement it.