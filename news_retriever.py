"""
news_retriever.py
=================
Handles API requests to NewsAPI to fetch news articles on specific topics.
Returns LangChain Document objects for downstream embedding and summarization.
"""

import os
import hashlib
import requests
from typing import List, Dict, Any
from langchain_core.documents import Document

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


def _stable_id(url: str) -> str:
    """Generate a deterministic short ID from a URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def fetch_news(
    topic: str,
    page_size: int = 10,
    language: str = "en",
    sort_by: str = "publishedAt",
) -> List[Document]:
    """
    Fetch news articles from NewsAPI for a given topic.

    Args:
        topic: Search query / topic string.
        page_size: Number of articles to retrieve (max 100 for free tier).
        language: ISO 639-1 language code (default: "en").
        sort_by: Sort order — "publishedAt", "relevancy", or "popularity".

    Returns:
        A list of LangChain Document objects with article content and metadata.

    Raises:
        RuntimeError: If the NEWSAPI_KEY environment variable is not set.
        requests.HTTPError: If the API returns a non-2xx status.
    """
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing NEWSAPI_KEY environment variable. "
            "Sign up at https://newsapi.org/register to get a free key."
        )

    params = {
        "q": topic,
        "pageSize": page_size,
        "language": language,
        "sortBy": sort_by,
        "apiKey": api_key,
    }

    response = requests.get(NEWS_ENDPOINT, params=params, timeout=30)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()

    docs: List[Document] = []
    for article in data.get("articles", []):
        url = article.get("url") or ""
        title = article.get("title") or ""
        desc = article.get("description") or ""
        content = article.get("content") or ""

        # Combine fields into a single text block for embedding / summarization
        text = f"TITLE: {title}\n\nDESCRIPTION: {desc}\n\nCONTENT: {content}".strip()

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "id": _stable_id(url) if url else None,
                    "source": (article.get("source") or {}).get("name"),
                    "author": article.get("author"),
                    "publishedAt": article.get("publishedAt"),
                    "url": url,
                    "topic": topic,
                },
            )
        )
    return docs
