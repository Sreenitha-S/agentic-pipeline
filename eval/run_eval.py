"""
Evaluation harness.

Runs every query in test_queries.json through the pipeline, records:
  - whether the router's routing decision matched the expected route,
  - latency of the tool call step specifically (as required by the assignment),
  - total end-to-end latency,
and writes a results.md table plus a results.json with full traces for manual answer-quality review.

Usage:
    python eval/run_eval.py --router-version v2
    python eval/run_eval.py --router-version v1   # compare against the earlier prompt version
    python eval/run_eval.py --retriever embeddings   # use the semantic retriever instead of TF-IDF
"""

import sys
import os
import json
import time
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from controller import Controller  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def load_queries():
    with open(os.path.join(HERE, "test_queries.json"), encoding="utf-8") as f:
        return json.load(f)


def run(router_version: str, retriever_kind: str = "tfidf", retries: int = 2, retry_delay_s: float = 3.0):
    controller = Controller(router_version=router_version, retriever_kind=retriever_kind)
    queries = load_queries()
    rows = []
    full_states = []
    n_errors = 0

    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {q['question']}")
        state = None
        last_error = None

        for attempt in range(1, retries + 2):  # e.g. retries=2 -> up to 3 attempts total
            try:
                state = controller.run(q["question"])
                break
            except Exception as e:
                last_error = e
                print(f"    attempt {attempt} failed: {e}")
                if attempt < retries + 1:
                    time.sleep(retry_delay_s)

        if state is None:
            # This query failed on every attempt (e.g. quota/rate-limit exhausted). Record the
            # failure and move on instead of losing every result gathered so far.
            n_errors += 1
            rows.append({
                "id": q["id"],
                "question": q["question"],
                "expected_route": q["expected_route"],
                "actual_route": "ERROR",
                "route_match": False,
                "tool_latency_ms": None,
                "total_latency_ms": None,
                "answer": f"[ERROR after {retries + 1} attempts: {last_error}]",
            })
            continue

        full_states.append(state)

        actual_route = "tool" if state["router_decision"].get("use_tool") else "kb"
        route_match = actual_route == q["expected_route"]

        tool_step = next((s for s in state["trace"] if s["step"] == "tool_call" and not s.get("skipped")), None)
        tool_latency = tool_step["latency_ms"] if tool_step else None

        rows.append({
            "id": q["id"],
            "question": q["question"],
            "expected_route": q["expected_route"],
            "actual_route": actual_route,
            "route_match": route_match,
            "tool_latency_ms": tool_latency,
            "total_latency_ms": state["total_latency_ms"],
            "answer": state["answer"],
        })

    return rows, full_states


def write_results(rows, full_states, router_version, retriever_kind="tfidf"):
    n_correct = sum(1 for r in rows if r["route_match"])
    n_errors = sum(1 for r in rows if r["actual_route"] == "ERROR")
    accuracy = round(100 * n_correct / len(rows), 1) if rows else 0.0
    tool_latencies = [r["tool_latency_ms"] for r in rows if r["tool_latency_ms"] is not None]
    avg_tool_latency = round(sum(tool_latencies) / len(tool_latencies), 1) if tool_latencies else None
    total_latencies = [r["total_latency_ms"] for r in rows if r["total_latency_ms"] is not None]
    avg_total_latency = round(sum(total_latencies) / len(total_latencies), 1) if total_latencies else None

    suffix = router_version if retriever_kind == "tfidf" else f"{router_version}_{retriever_kind}"
    md_path = os.path.join(HERE, f"results_{suffix}.md")
    json_path = os.path.join(HERE, f"results_{suffix}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Evaluation Results (router {router_version}, retriever {retriever_kind})\n\n")
        f.write(f"- Routing accuracy vs expected: **{n_correct}/{len(rows)} ({accuracy}%)**\n")
        if n_errors:
            f.write(f"- ⚠️ **{n_errors} quer{'y' if n_errors == 1 else 'ies'} failed** "
                    f"(e.g. provider rate limit/quota) after retries -- see table below.\n")
        f.write(f"- Avg tool-call latency (when tool used): **{avg_tool_latency} ms**\n")
        f.write(f"- Avg total end-to-end latency: **{avg_total_latency} ms**\n\n")
        f.write("| # | Question | Expected route | Actual route | Match | Tool latency (ms) | Total latency (ms) |\n")
        f.write("|---|----------|-----------------|--------------|-------|--------------------|--------------------|\n")
        for r in rows:
            f.write(
                f"| {r['id']} | {r['question']} | {r['expected_route']} | {r['actual_route']} | "
                f"{'✅' if r['route_match'] else '❌'} | {r['tool_latency_ms'] or '-'} | {r['total_latency_ms'] or '-'} |\n"
            )
        f.write("\n## Answers (for manual quality review)\n\n")
        for r in rows:
            f.write(f"**Q{r['id']}: {r['question']}**\n\n> {r['answer']}\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_states, f, indent=2, default=str)

    print(f"Wrote {md_path} and {json_path}")
    print(f"Routing accuracy: {n_correct}/{len(rows)} ({accuracy}%)")
    if n_errors:
        print(f"WARNING: {n_errors} queries failed after retries -- check results_{suffix}.md for details")
    print(f"Avg tool latency: {avg_tool_latency} ms | Avg total latency: {avg_total_latency} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-version", default="v2", choices=["v1", "v2"])
    parser.add_argument("--retriever", default="tfidf", choices=["tfidf", "embeddings"])
    args = parser.parse_args()
    rows, full_states = run(args.router_version, retriever_kind=args.retriever)
    write_results(rows, full_states, args.router_version, retriever_kind=args.retriever)
