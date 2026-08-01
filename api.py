"""
FastAPI backend for the React UI. Thin wrapper around src/controller.py -- no pipeline logic
lives here, this file only translates HTTP requests into Controller.run() calls and back.

Run with:
    uvicorn api:app --reload --port 8000

The React dev server (default http://localhost:5173) talks to this over CORS.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from controller import Controller
from llm_client import get_llm

app = FastAPI(title="CloudNest Agent Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev only -- tighten this if you ever deploy publicly
    allow_methods=["*"],
    allow_headers=["*"],
)

# Controllers are cheap-ish to build (loads KB + vectorizer) but not free, so cache one per
# (router_version, retriever_kind) combination instead of rebuilding on every request.
_controller_cache = {}


def get_controller(router_version: str, retriever_kind: str) -> Controller:
    key = (router_version, retriever_kind)
    if key not in _controller_cache:
        _controller_cache[key] = Controller(router_version=router_version, retriever_kind=retriever_kind)
    return _controller_cache[key]


class QueryRequest(BaseModel):
    question: str
    router_version: str = "v2"
    retriever_kind: str = "tfidf"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/provider")
def provider():
    """Zero-cost check of which LLM provider is active -- mirrors check_provider.py."""
    llm = get_llm()
    name = type(llm).__name__
    return {
        "provider": name,
        "is_mock": name == "MockLLM",
        "env_detected": {
            "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "GROQ_API_KEY": bool(os.environ.get("GROQ_API_KEY")),
            "HF_TOKEN": bool(os.environ.get("HF_TOKEN")),
        },
    }


@app.post("/api/query")
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")
    if req.router_version not in ("v1", "v2"):
        raise HTTPException(status_code=400, detail="router_version must be 'v1' or 'v2'")
    if req.retriever_kind not in ("tfidf", "embeddings"):
        raise HTTPException(status_code=400, detail="retriever_kind must be 'tfidf' or 'embeddings'")

    try:
        controller = get_controller(req.router_version, req.retriever_kind)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize controller: {e}")

    try:
        state = controller.run(req.question)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pipeline error: {e}")

    return state


@app.get("/api/kb-docs")
def list_kb_docs():
    """Lists the KB documents so the UI can show what's actually in the knowledge base."""
    controller = get_controller("v2", "tfidf")
    return {
        "doc_ids": controller.retriever.doc_ids,
        "count": len(controller.retriever.doc_ids),
    }
