import chainlit as cl
from dotenv import load_dotenv
import os 
from openai import OpenAI
from qdrant_client import QdrantClient
from parse import parse_pdf 
from query_parser import parse_query
from retrieve import retrieve
from generate import generate_response
from chunk import chunk
from ingest import ingest_chunks, setup_collection

COLLECTION_NAME = "eco_zoning"

@cl.on_chat_start
async def on_chat_start():
    load_dotenv()
    
    qdrant_client = QdrantClient(":memory:")
    openai_client = OpenAI()
    
    pdf_path = "data/raw/LA-zoning-regulations.pdf"
    text = parse_pdf(pdf_path)
    chunks = chunk(text)
    
    setup_collection(qdrant_client, COLLECTION_NAME)
    ingest_chunks(qdrant_client, COLLECTION_NAME, openai_client, chunks)
    
    await cl.Message(content="Welcome to the LA Zoning Assistant! Ask me anything about LA zoning regulations.").send()
    
    cl.user_session.set("qdrant_client", qdrant_client)
    cl.user_session.set("openai_client", openai_client)
    cl.user_session.set("collection_name", COLLECTION_NAME)

@cl.on_message
async def on_message(message: cl.Message):
    qdrant_client = cl.user_session.get("qdrant_client")
    openai_client = cl.user_session.get("openai_client")
    collection_name = cl.user_session.get("collection_name")
    
    await cl.Message(content="Searching zoning documents...").send()
    
    zone_filter = parse_query(message.content, openai_client)
    zone = zone_filter.zone
    
    if zone is None:
        await cl.Message(content="Could not identify a zone in your query. Please mention a zone code like R1, C2, or A1.").send()
        return
        
    hits = retrieve(message.content, zone, qdrant_client, openai_client, collection_name, top_k = 20)
    response = generate_response(message.content, hits, openai_client)
    
    await cl.Message(content=response).send()
