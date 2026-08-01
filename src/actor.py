"""
Actor component: the one tool this agent can execute.

Chosen tool: local CSV acting as an API (`data/prices.csv`), simulating a live pricing/usage
backend. Chosen over live web search / a real REST API for the assignment because it is:
  - fully reproducible for grading (no network flakiness or rate limits),
  - still exercises the same "agent calls an external system that can be queried by a key
    and returns fresh, structured data" pattern as a real API would.
The function signature is written so swapping in `requests.get(...)` against a real FastAPI
pricing endpoint is a one-line change (see `pricing_lookup_via_rest_api` stub at the bottom).
"""

import csv
import os
import time


class PricingTool:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.rows = self._load()

    def _load(self):
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["plan_name"].lower(): row for row in reader}

    def lookup(self, plan_name: str):
        """Simulates a network call: small artificial latency so eval latency numbers are meaningful."""
        start = time.time()
        time.sleep(0.05)  # simulated network round-trip
        plan = self.rows.get(plan_name.strip().lower())
        latency_ms = round((time.time() - start) * 1000, 1)
        if plan is None:
            return {"found": False, "error": f"No plan named '{plan_name}'"}, latency_ms
        return {"found": True, **plan}, latency_ms


def pricing_lookup_via_rest_api(plan_name: str, base_url: str = "http://localhost:8000"):
    """
    Stub showing how this tool would be swapped for a real REST API call, e.g. a self-built
    FastAPI service backed by the same CSV. Left unused by default (see docstring above).
    """
    import requests  # local import: optional dependency, only needed on this path
    resp = requests.get(f"{base_url}/pricing/{plan_name}", timeout=5)
    resp.raise_for_status()
    return resp.json()
