# Eco-Zoning RAG — Claude Code Instructions

## Project summary
A retrieval-augmented generation system that answers zoning and climate
questions for specific city neighborhoods. Currently uses LA zoning regulations
as the data source. Users query in natural language; the system extracts the
zone, retrieves relevant chunks (hybrid BM25 + vector search, reranked), and
generates a grounded answer.

## Stack
- Python 3.13 (.venv committed as the project interpreter; CI runs 3.13 too)
- qdrant-client (in-memory for dev)
- openai (embeddings: text-embedding-3-small, generation: gpt-4o)
- cohere (rerank-english-v3.0 — reranks fused hybrid results)
- rank-bm25 (keyword search)
- pdfplumber (table-aware PDF parsing — tables and prose extracted separately)
- instructor (structured output for query parsing)
- chainlit (chat UI)
- python-dotenv
- pytest, pre-commit

## Project structure
eco-zoning-rag/
├── src/
│   ├── embed.py           # get_embedding() — text to vector
│   ├── ingest.py          # setup_collection(), ingest_chunks()
│   ├── parse.py           # parse_pdf() — PDF to list[dict] content blocks (text/table)
│   ├── chunk.py           # chunk() — blocks to list of dicts with metadata
│   ├── retrieve.py        # retrieve() — zone-filtered vector search
│   ├── hybrid_retrieve.py # hybrid_retrieve() — BM25 + vector + RRF fusion
│   ├── rerank.py          # rerank() — Cohere reranks fused hybrid results
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
│   ├── conftest.py        # fake_openai_client fixture — no real API calls in tests
│   └── test_retrieve.py
├── .github/workflows/     # ci.yml — pytest on push/PR to main (no API keys needed)
├── .claude/
│   ├── settings.json      # PreToolUse hook: blocks git commit/push until tests pass
│   └── hooks/              # hook scripts
├── .pre-commit-config.yaml # local pytest gate at pre-commit + pre-push stages
├── .env                   # OPENAI_API_KEY, COHERE_API_KEY (gitignored)
└── conftest.py            # adds src/ to pytest path

## Coding conventions
- All clients (OpenAI, QdrantClient, cohere.Client) injected as parameters — never instantiated inside functions
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
- Tests: pytest tests/ -v (mocked OpenAI client — no API key needed, no cost)
- Pre-commit hooks (installed): pre-commit run --all-files
- Any module standalone: python src/module.py (from project root)

## Testing & CI/CD
- tests/conftest.py provides fake_openai_client, a duck-typed fake for
  client.embeddings.create() with deterministic hash-seeded vectors. Tests
  never hit the network or need OPENAI_API_KEY/COHERE_API_KEY.
- GitHub Actions (.github/workflows/ci.yml) runs pytest on every push/PR to main.
- pre-commit (.pre-commit-config.yaml) runs pytest at both the pre-commit and
  pre-push git hook stages. On Windows, the entry path uses doubled backslashes
  (.venv\\Scripts\\python.exe) — forward slashes fail Windows' CreateProcess
  relative-path resolution, and single backslashes get eaten by pre-commit's
  shlex parsing.
- A Claude Code PreToolUse hook (.claude/settings.json +
  .claude/hooks/check_tests_before_git.py) intercepts git commit/git push run
  via the Bash tool and denies them if pytest fails — applies to Claude Code
  itself, not just human commits.

## Current data source
LA Zoning Regulations — data/raw/LA-zoning-regulations.pdf
17 pages, 108 chunks (48 structured table-row chunks across 45 zones, 60 prose
chunks). parse.py extracts tables and prose as separate content blocks via
pdfplumber; table chunks get their zone from column 0 (falling back to column
1 when empty) instead of regex, so zone tagging on table rows is exact.

## Known issues
- Qdrant payload indexes have no effect in memory mode — expected warning, ignore it
- Text-block chunks (prose, not table rows) still tag zone via regex and can
  legitimately be "UNKNOWN" (~32 of 108 chunks) when no zone code appears in
  that paragraph — this is expected, not a bug
- Grid-shaped tables that don't fit the zone-row structure (e.g. the height-
  district tables on pages 8-10) get flattened into text blocks rather than
  structured table blocks — parse.py can't build a header mapping for them
- top_k=20 needed for reliable retrieval of height-related R1 chunks
- requirements.txt must stay UTF-8 (pip on Linux CI can't read UTF-16) —
  watch for this if re-freezing it from a Windows PowerShell shell without
  specifying -Encoding utf8

## What not to do
- Do not use langchain or llamaindex unless explicitly asked (langchain-text-splitters is the one exception, used in chunk.py)
- Do not instantiate clients inside functions
- Do not use global variables outside main.py and app.py
- Do not add dependencies not in requirements.txt without flagging it
- Do not write placeholder comments — implement fully
- Do not use src. prefix in imports
- Do not make real OpenAI/Cohere API calls in tests — use the fake_openai_client fixture in tests/conftest.py
