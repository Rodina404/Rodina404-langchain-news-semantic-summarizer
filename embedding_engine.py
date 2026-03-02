"""
embedding_engine.py
===================
Creates and manages article embeddings using Google Gemini,
stores them in a Chroma vector database, and performs semantic search.
"""

import os
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── Embedding Model ────────────────────────────────────────────────────

def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """
    Return the Google Gemini embedding model.
    Requires the GOOGLE_API_KEY environment variable.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY environment variable. "
            "Get one at https://aistudio.google.com/app/apikey"
        )
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )


# ── Vector Store ───────────────────────────────────────────────────────

def build_vector_store(
    docs: List[Document],
    embedding_model: GoogleGenerativeAIEmbeddings,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    persist_directory: str = "./chroma_db",
) -> Chroma:
    """
    Split documents into chunks, embed them, and store in Chroma.

    Args:
        docs: List of LangChain Documents (from news_retriever).
        embedding_model: The embedding model instance.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        persist_directory: Where to persist the Chroma database on disk.

    Returns:
        A Chroma vector store populated with the document chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)

    # Filter out empty chunks
    chunks = [c for c in chunks if c.page_content.strip()]

    if not chunks:
        raise ValueError("No non-empty chunks produced from the documents.")

    vectordb = Chroma(
        collection_name="news_articles",
        embedding_function=embedding_model,
        persist_directory=persist_directory,
    )
    vectordb.add_documents(chunks)
    return vectordb


# ── Semantic Search ────────────────────────────────────────────────────

def semantic_search(
    vectordb: Chroma,
    query: str,
    k: int = 5,
) -> List[Document]:
    """
    Perform similarity search against the vector store.

    Args:
        vectordb: A populated Chroma vector store.
        query: The user's natural-language question.
        k: Number of top results to return.

    Returns:
        A list of the top-k most relevant Document chunks.
    """
    return vectordb.similarity_search(query, k=k)
