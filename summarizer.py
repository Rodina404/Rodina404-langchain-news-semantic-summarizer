"""
summarizer.py
=============
Implements two LangChain summarization chain types:
  • brief  — "stuff" chain  → concise 1-2 sentence summary
  • detailed — "map_reduce" chain → full paragraph summary
"""

import os
from typing import List, Literal
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_classic.chains.summarize import load_summarize_chain


# ── LLM ────────────────────────────────────────────────────────────────

def get_llm() -> ChatGroq:
    """
    Return a Groq-hosted LLM (LLaMA 3.1 8B Instant).
    Requires the GROQ_API_KEY environment variable.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY environment variable. "
            "Get one at https://console.groq.com/keys"
        )
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_retries=2,
        api_key=api_key,
    )


# ── Summarization Chains ──────────────────────────────────────────────

def summarize_docs(
    docs: List[Document],
    mode: Literal["brief", "detailed"] = "brief",
) -> str:
    """
    Summarize a list of retrieved documents.

    Args:
        docs: Documents returned by semantic search.
        mode: "brief" for 1-2 sentences (stuff chain),
              "detailed" for a full paragraph (map_reduce chain).

    Returns:
        The generated summary string.
    """
    llm = get_llm()

    if mode == "brief":
        chain_type = "stuff"
        instruction = "Summarize in 1-2 sentences. Be very concise."
    else:
        chain_type = "map_reduce"
        instruction = "Write a detailed paragraph summary (5-8 sentences)."

    chain = load_summarize_chain(llm, chain_type=chain_type)

    # Prepend the instruction as an extra document so the chain sees it
    prompt_doc = Document(page_content=f"INSTRUCTION: {instruction}")
    result = chain.run([prompt_doc] + docs)
    return result
