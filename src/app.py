import chainlit as cl
from dotenv import load_dotenv
import os
import cohere
from openai import OpenAI
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from parse import parse_pdf
from query_parser import parse_query
from hybrid_retrieve import hybrid_retrieve
from generate import generate_response
from chunk import chunk
from ingest import ingest_chunks, setup_collection
from rerank import rerank

COLLECTION_NAME = "eco_zoning"

@cl.on_chat_start
async def on_chat_start():
    load_dotenv()
    
    qdrant_client = QdrantClient(":memory:")
    openai_client = OpenAI()
    cohere_client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    blocks = parse_pdf(pdf_path)
    chunks = chunk(blocks, source=os.path.basename(pdf_path))
    
    setup_collection(qdrant_client, COLLECTION_NAME)
    ingest_chunks(qdrant_client, COLLECTION_NAME, openai_client, chunks)

    bm25_index = BM25Okapi([c["text"].split() for c in chunks])

    await cl.Message(content="Welcome to the LA Zoning Assistant! Ask me anything about LA zoning regulations.").send()

    cl.user_session.set("qdrant_client", qdrant_client)
    cl.user_session.set("openai_client", openai_client)
    cl.user_session.set("cohere_client", cohere_client)
    cl.user_session.set("collection_name", COLLECTION_NAME)
    cl.user_session.set("bm25_index", bm25_index)
    cl.user_session.set("chunks", chunks)

@cl.on_message
async def on_message(message: cl.Message):
    qdrant_client = cl.user_session.get("qdrant_client")
    openai_client = cl.user_session.get("openai_client")
    cohere_client = cl.user_session.get("cohere_client")
    collection_name = cl.user_session.get("collection_name")
    bm25_index = cl.user_session.get("bm25_index")
    chunks = cl.user_session.get("chunks")

    await cl.Message(content="Searching zoning documents...").send()

    zone_filter = parse_query(message.content, openai_client)
    zone = zone_filter.zone

    if zone is None:
        await cl.Message(content="Could not identify a zone in your query. Please mention a zone code like R1, C2, or A1.").send()
        return

    hits = hybrid_retrieve(message.content, zone, qdrant_client, openai_client, collection_name, bm25_index, chunks, top_k=20)
    reranked_hits = rerank(message.content, hits, cohere_client, top_n=5)
    response = generate_response(message.content, reranked_hits, openai_client)
    
    await cl.Message(content=response).send()
