"""
user_manager.py
===============
Tracks user preferences, saved topics, and search history
using a simple JSON file for persistence.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

USER_DATA_PATH = "user_data.json"

# ── Default Structure ─────────────────────────────────────────────────

_DEFAULT_DATA: Dict[str, Any] = {
    "saved_topics": [],
    "preferences": {
        "default_summary_mode": "brief",   # "brief" or "detailed"
    },
    "history": [],
}


# ── Helpers ───────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ── Load / Save ───────────────────────────────────────────────────────

def load_user_data(path: str = USER_DATA_PATH) -> Dict[str, Any]:
    """Load user data from JSON file, or return defaults if missing."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(_DEFAULT_DATA))  # deep copy


def save_user_data(data: Dict[str, Any], path: str = USER_DATA_PATH) -> None:
    """Persist user data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Topics ────────────────────────────────────────────────────────────

def save_topic(data: Dict[str, Any], topic: str) -> None:
    """Add a topic to saved topics (no duplicates)."""
    if topic and topic not in data["saved_topics"]:
        data["saved_topics"].append(topic)


def remove_topic(data: Dict[str, Any], topic: str) -> None:
    """Remove a topic from saved topics."""
    if topic in data["saved_topics"]:
        data["saved_topics"].remove(topic)


def get_saved_topics(data: Dict[str, Any]) -> List[str]:
    """Return the list of saved topics."""
    return data.get("saved_topics", [])


# ── Preferences ───────────────────────────────────────────────────────

def set_default_mode(data: Dict[str, Any], mode: str) -> None:
    """Set the default summary mode ('brief' or 'detailed')."""
    data.setdefault("preferences", {})["default_summary_mode"] = mode


def get_default_mode(data: Dict[str, Any]) -> str:
    """Get the current default summary mode."""
    return data.get("preferences", {}).get("default_summary_mode", "brief")


# ── History ───────────────────────────────────────────────────────────

def add_history(
    data: Dict[str, Any],
    topic: str,
    mode: str,
    user_query: str,
    k: int,
    num_articles: int,
) -> None:
    """Append a search entry to the history log."""
    data.setdefault("history", []).append({
        "ts": _now_iso(),
        "topic": topic,
        "mode": mode,
        "user_query": user_query,
        "top_k": k,
        "articles_fetched": num_articles,
    })


def get_history(data: Dict[str, Any], n: int = 10) -> List[Dict[str, Any]]:
    """Return the last *n* history entries."""
    return data.get("history", [])[-n:]
