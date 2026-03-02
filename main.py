"""
main.py
=======
Command-line interface for the News Semantic Summarizer.
Provides a colourful interactive menu to search news, save topics,
manage preferences, and review search history.
"""

import sys
from dotenv import load_dotenv

from news_retriever import fetch_news
from embedding_engine import get_embedding_model, build_vector_store, semantic_search
from summarizer import summarize_docs
from user_manager import (
    load_user_data, save_user_data,
    save_topic, get_saved_topics,
    add_history, get_history,
    set_default_mode, get_default_mode,
)

# Load .env file so API keys are available as environment variables
load_dotenv()

# ── ANSI colours ──────────────────────────────────────────────────────
GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
PURPLE = "\033[95m"
RESET  = "\033[0m"

MENU = f"""
{PURPLE}╔══════════════════════════════════════════╗
║   📰  News Semantic Summarizer  📰      ║
╚══════════════════════════════════════════╝{RESET}
  {CYAN}1){RESET} Search news by topic
  {CYAN}2){RESET} Save a topic
  {CYAN}3){RESET} View saved topics
  {CYAN}4){RESET} Set default summary mode (brief / detailed)
  {CYAN}5){RESET} View search history
  {RED}q){RESET} Quit
"""


def main() -> None:
    user_data = load_user_data()
    embedding_model = get_embedding_model()

    print(f"\n{PURPLE}{'═' * 44}")
    print(f"  Welcome to the News Semantic Summarizer!")
    print(f"{'═' * 44}{RESET}")
    print(f"{YELLOW}Type 'q' at any prompt to exit.{RESET}")

    while True:
        print(MENU)
        choice = input(f"{GREEN}Choose an option ▸ {RESET}").strip().lower()

        if choice == "q":
            print(f"\n{RED}Goodbye! 👋{RESET}\n")
            break

        # ── 1) Search ─────────────────────────────────────────────
        if choice == "1":
            topic = input(f"{GREEN}Enter topic to search: {RESET}").strip()
            if topic.lower() == "q":
                break

            default = get_default_mode(user_data)
            mode = input(
                f"{GREEN}Summary type (brief/detailed) [default={default}]: {RESET}"
            ).strip().lower() or default

            if mode == "q":
                break
            if mode not in ("brief", "detailed"):
                print(f"{YELLOW}Invalid choice — using '{default}'.{RESET}")
                mode = default

            user_query = input(
                f"{GREEN}Ask your question about this topic: {RESET}"
            ).strip()
            if user_query.lower() == "q":
                break

            try:
                print(f"\n{CYAN}⏳ Fetching articles…{RESET}")
                articles = fetch_news(topic, page_size=10)
                if not articles:
                    print(f"{RED}No articles found. Try another topic.\n{RESET}")
                    continue

                print(f"{CYAN}⏳ Building vector store…{RESET}")
                vectordb = build_vector_store(articles, embedding_model)

                k = 6
                print(f"{CYAN}⏳ Performing semantic search (top-{k})…{RESET}")
                retrieved = semantic_search(vectordb, user_query, k=k)

                print(f"\n{CYAN}⏳ Generating {mode} summary…{RESET}\n")
                summary = summarize_docs(retrieved, mode)

                print(f"{PURPLE}{'─' * 44}")
                print(f"  SUMMARY ({mode.upper()})")
                print(f"{'─' * 44}{RESET}")
                print(summary)
                print(f"{PURPLE}{'─' * 44}{RESET}\n")

                add_history(user_data, topic, mode, user_query, k, len(articles))
                save_user_data(user_data)
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}\n")

        # ── 2) Save topic ─────────────────────────────────────────
        elif choice == "2":
            topic = input(f"{GREEN}Topic to save: {RESET}").strip()
            if topic.lower() == "q":
                break
            if topic:
                save_topic(user_data, topic)
                save_user_data(user_data)
                print(f"{CYAN}✔ Saved topic: {topic}{RESET}")

        # ── 3) View saved topics ──────────────────────────────────
        elif choice == "3":
            topics = get_saved_topics(user_data)
            if not topics:
                print(f"{YELLOW}No saved topics yet.{RESET}")
            else:
                print(f"{CYAN}Saved topics:{RESET}")
                for i, t in enumerate(topics, 1):
                    print(f"  {i}. {t}")

        # ── 4) Set default mode ───────────────────────────────────
        elif choice == "4":
            new_mode = input(
                f"{GREEN}Set default mode (brief/detailed): {RESET}"
            ).strip().lower()
            if new_mode == "q":
                break
            if new_mode not in ("brief", "detailed"):
                print(f"{YELLOW}Invalid mode. No change.{RESET}")
            else:
                set_default_mode(user_data, new_mode)
                save_user_data(user_data)
                print(f"{CYAN}✔ Default summary mode set to: {new_mode}{RESET}")

        # ── 5) View history ───────────────────────────────────────
        elif choice == "5":
            history = get_history(user_data, n=10)
            if not history:
                print(f"{YELLOW}No history yet.{RESET}")
            else:
                print(f"{CYAN}Recent searches:{RESET}")
                for item in history:
                    ts = item.get("ts", "")
                    t = item.get("topic", "")
                    m = item.get("mode", "")
                    q = item.get("user_query", "")
                    print(f"  [{ts}] topic='{t}' mode='{m}' query='{q}'")

        else:
            print(f"{YELLOW}Invalid option. Try again.{RESET}")


if __name__ == "__main__":
    main()
