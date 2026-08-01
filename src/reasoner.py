"""
Reasoner component: loads prompt templates and calls the LLM.

Keeps two responsibilities separate:
  1. `route()` -- decide KB-only vs KB+tool, using the router prompt (v1 or v2).
  2. `synthesize()` -- produce the final natural-language answer, using the answer prompt.
Prompt versions live as plain text files under prompts/ so they can be diffed/reviewed like
code, and so the pipeline can be run with --router-version v1 or v2 to compare behavior
(see eval/run_eval.py and the README section on prompt iteration).
"""

import json
import os

from llm_client import timed_complete

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompt(name: str) -> str:
    with open(os.path.join(PROMPTS_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


class Reasoner:
    def __init__(self, llm, router_version: str = "v2"):
        self.llm = llm
        self.router_template = _load_prompt(f"router_{router_version}.txt")
        self.answer_template = _load_prompt("answer_v1.txt")

    def route(self, question: str, kb_results: list):
        kb_context = "\n\n".join(f"[{r['doc_id']}] {r['text']}" for r in kb_results)
        prompt = self.router_template.replace("{question}", question).replace("{kb_context}", kb_context)
        raw, latency_ms = timed_complete(self.llm, prompt, max_tokens=200)
        try:
            cleaned = raw.strip().strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            decision = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fail safe: if the router output isn't valid JSON, don't crash the pipeline --
            # default to not using the tool and log the raw output for debugging.
            decision = {"use_tool": False, "tool_query": "", "reason": f"unparsed router output: {raw}"}
        return decision, raw, latency_ms

    def synthesize(self, question: str, kb_results: list, tool_output: dict | None):
        kb_context = "\n\n".join(f"[{r['doc_id']}] {r['text']}" for r in kb_results)
        tool_str = json.dumps(tool_output) if tool_output else "(empty - tool not called)"
        prompt = (
            self.answer_template.replace("{question}", question)
            .replace("{kb_context}", kb_context)
            .replace("{tool_output}", tool_str)
        )
        answer, latency_ms = timed_complete(self.llm, prompt, max_tokens=400)
        return answer.strip(), latency_ms
