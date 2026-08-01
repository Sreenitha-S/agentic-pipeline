"""
CLI entry point for the mini agentic pipeline.

Usage:
    python main.py "How much does the Team plan cost per month?"
    python main.py "How much does the Team plan cost per month?" --router-version v1
    python main.py "How much does the Team plan cost per month?" --retriever embeddings
    python main.py --interactive
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from controller import Controller, pretty_print  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Mini agentic pipeline: KB retriever + LLM reasoner + tool actor")
    parser.add_argument("question", nargs="?", help="Question to ask the pipeline")
    parser.add_argument("--router-version", default="v2", choices=["v1", "v2"], help="Which router prompt version to use")
    parser.add_argument("--top-k", type=int, default=3, help="Number of KB passages to retrieve")
    parser.add_argument("--retriever", default="tfidf", choices=["tfidf", "embeddings"],
                         help="Retriever backend: 'tfidf' (default, keyword-based) or "
                              "'embeddings' (local sentence-transformers semantic search)")
    parser.add_argument("--interactive", action="store_true", help="Run an interactive loop")
    parser.add_argument("--json", action="store_true", help="Print raw JSON state instead of pretty trace")
    args = parser.parse_args()

    controller = Controller(router_version=args.router_version, top_k=args.top_k, retriever_kind=args.retriever)

    if args.interactive:
        print("Interactive mode. Type 'exit' to quit.")
        while True:
            q = input("\n> ")
            if q.strip().lower() in ("exit", "quit"):
                break
            state = controller.run(q)
            if args.json:
                print(json.dumps(state, indent=2, default=str))
            else:
                pretty_print(state)
        return

    if not args.question:
        parser.print_help()
        return

    state = controller.run(args.question)
    if args.json:
        print(json.dumps(state, indent=2, default=str))
    else:
        pretty_print(state)


if __name__ == "__main__":
    main()

