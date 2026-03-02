"""
app.py
======
Flask web application providing a beautiful purple-themed UI
for the News Semantic Summarizer.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from news_retriever import fetch_news
from embedding_engine import get_embedding_model, build_vector_store, semantic_search
from summarizer import summarize_docs
from user_manager import (
    load_user_data, save_user_data,
    save_topic, remove_topic, get_saved_topics,
    add_history, get_history,
    set_default_mode, get_default_mode,
)

load_dotenv()

app = Flask(__name__)
embedding_model = None  # lazy init


def _get_embedding_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = get_embedding_model()
    return embedding_model


# ── Pages ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API: Search & Summarise ──────────────────────────────────────────

@app.route("/api/search")
def api_search():
    topic = request.args.get("topic", "").strip()
    mode = request.args.get("mode", "brief").strip()
    query = request.args.get("query", "").strip()

    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    if not query:
        query = f"What are the latest updates on {topic}?"
    if mode not in ("brief", "detailed"):
        mode = "brief"

    try:
        articles = fetch_news(topic, page_size=10)
        if not articles:
            return jsonify({"error": "No articles found for this topic."}), 404

        em = _get_embedding_model()
        vectordb = build_vector_store(articles, em)

        k = 6
        retrieved = semantic_search(vectordb, query, k=k)
        summary = summarize_docs(retrieved, mode)

        # Persist history
        data = load_user_data()
        add_history(data, topic, mode, query, k, len(articles))
        save_user_data(data)

        # Build article metadata for the UI
        article_cards = []
        for doc in retrieved:
            m = doc.metadata
            article_cards.append({
                "title": (doc.page_content.split("\n")[0]
                          .replace("TITLE: ", "")
                          if doc.page_content else ""),
                "source": m.get("source", ""),
                "author": m.get("author", ""),
                "publishedAt": m.get("publishedAt", ""),
                "url": m.get("url", ""),
            })

        return jsonify({
            "summary": summary,
            "mode": mode,
            "topic": topic,
            "articles": article_cards,
            "total_fetched": len(articles),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── API: Topics ──────────────────────────────────────────────────────

@app.route("/api/topics", methods=["GET"])
def api_get_topics():
    data = load_user_data()
    return jsonify({"topics": get_saved_topics(data)})


@app.route("/api/topics", methods=["POST"])
def api_save_topic():
    body = request.get_json(force=True)
    topic = body.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    data = load_user_data()
    save_topic(data, topic)
    save_user_data(data)
    return jsonify({"topics": get_saved_topics(data)})


@app.route("/api/topics", methods=["DELETE"])
def api_delete_topic():
    body = request.get_json(force=True)
    topic = body.get("topic", "").strip()
    data = load_user_data()
    remove_topic(data, topic)
    save_user_data(data)
    return jsonify({"topics": get_saved_topics(data)})


# ── API: History ─────────────────────────────────────────────────────

@app.route("/api/history")
def api_history():
    data = load_user_data()
    return jsonify({"history": get_history(data, n=20)})


# ── API: Preferences ────────────────────────────────────────────────

@app.route("/api/preferences", methods=["GET"])
def api_get_prefs():
    data = load_user_data()
    return jsonify({"default_mode": get_default_mode(data)})


@app.route("/api/preferences", methods=["POST"])
def api_set_prefs():
    body = request.get_json(force=True)
    mode = body.get("default_mode", "brief")
    if mode not in ("brief", "detailed"):
        return jsonify({"error": "Mode must be 'brief' or 'detailed'"}), 400
    data = load_user_data()
    set_default_mode(data, mode)
    save_user_data(data)
    return jsonify({"default_mode": mode})


# ── Run ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
