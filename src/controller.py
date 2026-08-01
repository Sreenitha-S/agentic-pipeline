"""
Controller: orchestrates Retriever -> Reasoner(router) -> Actor(tool, conditional) ->
Reasoner(synthesize), passing a shared state dict between steps and producing a full
step-by-step trace/log for every query.
"""

import os
import time
import json

from retriever import get_retriever
from reasoner import Reasoner
from actor import PricingTool
from llm_client import get_llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, "data", "kb")
PRICES_CSV = os.path.join(BASE_DIR, "data", "prices.csv")


class Controller:
    def __init__(self, router_version: str = "v2", top_k: int = 3, retriever_kind: str = "tfidf"):
        self.llm = get_llm()
        self.llm_provider_name = type(self.llm).__name__
        print(f"[controller] Active LLM provider: {self.llm_provider_name}")
        self.retriever = get_retriever(retriever_kind, KB_DIR)
        self.retriever_kind = type(self.retriever).__name__
        print(f"[controller] Active retriever: {self.retriever_kind}")
        self.reasoner = Reasoner(self.llm, router_version=router_version)
        self.tool = PricingTool(PRICES_CSV)
        self.top_k = top_k
        self.using_mock = self.llm_provider_name == "MockLLM"

    def run(self, question: str) -> dict:
        """Runs the full pipeline for one query. Returns shared state including full trace."""
        state = {
            "question": question,
            "trace": [],
            "using_mock_llm": self.using_mock,
            "retriever_kind": self.retriever_kind,
        }
        t0 = time.time()

        # Step 1: Retrieve
        step_start = time.time()
        kb_results = self.retriever.search(question, top_k=self.top_k)
        state["kb_results"] = kb_results
        state["trace"].append({
            "step": "retrieve",
            "latency_ms": round((time.time() - step_start) * 1000, 1),
            "hits": [{"doc_id": r["doc_id"], "score": r["score"]} for r in kb_results],
        })

        # Step 2: Reason (route: KB-only vs KB+tool)
        step_start = time.time()
        decision, raw_router_output, router_latency_ms = self.reasoner.route(question, kb_results)
        state["router_decision"] = decision
        state["trace"].append({
            "step": "route_decision",
            "latency_ms": router_latency_ms,
            "decision": decision,
            "raw_llm_output": raw_router_output,
        })

        # Step 3: Act (conditional tool call)
        tool_output = None
        if decision.get("use_tool"):
            step_start = time.time()
            tool_output, tool_latency_ms = self.tool.lookup(decision.get("tool_query", ""))
            state["tool_output"] = tool_output
            state["trace"].append({
                "step": "tool_call",
                "tool": "pricing_lookup",
                "query": decision.get("tool_query", ""),
                "latency_ms": tool_latency_ms,
                "result": tool_output,
            })
        else:
            state["tool_output"] = None
            state["trace"].append({"step": "tool_call", "skipped": True, "reason": "router decided KB was sufficient"})

        # Step 4: Synthesize final answer
        step_start = time.time()
        answer, answer_latency_ms = self.reasoner.synthesize(question, kb_results, tool_output)
        state["answer"] = answer
        state["trace"].append({
            "step": "synthesize_answer",
            "latency_ms": answer_latency_ms,
        })

        state["total_latency_ms"] = round((time.time() - t0) * 1000, 1)
        return state


def pretty_print(state: dict):
    print(f"\nQ: {state['question']}")
    print("-" * 70)
    for step in state["trace"]:
        print(f"  [{step['step']}] {json.dumps({k: v for k, v in step.items() if k != 'step'}, default=str)[:300]}")
    print("-" * 70)
    print(f"ANSWER: {state['answer']}")
    print(f"Total latency: {state['total_latency_ms']} ms | mock_llm={state['using_mock_llm']} | retriever={state['retriever_kind']}")


if __name__ == "__main__":
    controller = Controller()
    demo_questions = [
        "How much does the Team plan cost per month?",
        "What is 2FA support like on CloudNest?",
        "How many API calls are included in the Business plan?",
    ]
    for q in demo_questions:
        result = controller.run(q)
        pretty_print(result)
