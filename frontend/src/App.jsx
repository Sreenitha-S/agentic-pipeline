import { useEffect, useState, useCallback } from "react";
import Header from "./components/Header.jsx";
import QueryForm from "./components/QueryForm.jsx";
import Waterfall from "./components/Waterfall.jsx";
import AnswerCard from "./components/AnswerCard.jsx";
import RetrievalHits from "./components/RetrievalHits.jsx";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [question, setQuestion] = useState("");
  const [routerVersion, setRouterVersion] = useState("v2");
  const [retrieverKind, setRetrieverKind] = useState("tfidf");

  const [providerInfo, setProviderInfo] = useState(null);
  const [backendReachable, setBackendReachable] = useState(true);

  const [state, setState] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkProvider = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/provider`);
      if (!res.ok) throw new Error("bad response");
      const data = await res.json();
      setProviderInfo(data);
      setBackendReachable(true);
    } catch {
      setBackendReachable(false);
    }
  }, []);

  useEffect(() => {
    checkProvider();
  }, [checkProvider]);

  async function runQuery() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          router_version: routerVersion,
          retriever_kind: retrieverKind,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      const data = await res.json();
      setState(data);
      setHistory((h) => [{ question, data }, ...h].slice(0, 8));
      setBackendReachable(true);
    } catch (e) {
      setError(e.message || "Something went wrong");
      if (e.message?.includes("Failed to fetch")) setBackendReachable(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <Header providerInfo={providerInfo} backendReachable={backendReachable} />

      <main className="main">
        <section className="panel panel--form">
          <QueryForm
            question={question}
            setQuestion={setQuestion}
            routerVersion={routerVersion}
            setRouterVersion={setRouterVersion}
            retrieverKind={retrieverKind}
            setRetrieverKind={setRetrieverKind}
            onSubmit={runQuery}
            loading={loading}
          />
        </section>

        {!backendReachable && (
          <div className="banner banner--danger">
            Can&rsquo;t reach the API backend at <code>{API_BASE}</code>. Start it with{" "}
            <code>uvicorn api:app --reload --port 8000</code> from the project root, then reload this page.
          </div>
        )}

        {error && <div className="banner banner--danger">{error}</div>}

        {!state && backendReachable && !error && (
          <div className="empty-state">
            <p>Ask a question above to see the full agent trace: retrieval hits, the routing decision, the tool call (if any), and the final answer.</p>
          </div>
        )}

        {state && (
          <>
            <section className="panel">
              <RetrievalHits hits={state.trace.find((s) => s.step === "retrieve")?.hits} />
            </section>

            <section className="panel">
              <h2 className="section-title">Trace</h2>
              <Waterfall trace={state.trace} totalLatencyMs={state.total_latency_ms} />
            </section>

            <section className="panel panel--answer">
              <h2 className="section-title">Answer</h2>
              <AnswerCard state={state} />
            </section>
          </>
        )}

        {history.length > 1 && (
          <section className="panel panel--history">
            <h2 className="section-title">Recent queries</h2>
            <ul className="history-list">
              {history.slice(1).map((h, i) => (
                <li key={i}>
                  <button
                    className="history-item"
                    onClick={() => {
                      setState(h.data);
                      setQuestion(h.question);
                    }}
                  >
                    <span className={`badge badge--sm ${h.data.router_decision?.use_tool ? "badge--tool" : "badge--kb"}`}>
                      {h.data.router_decision?.use_tool ? "tool" : "kb"}
                    </span>
                    {h.question}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>

      <footer className="footer">
        Mini Agentic Pipeline &middot; CloudNest Support Assistant &middot; retriever: TF-IDF / embeddings &middot; reasoner: Anthropic / OpenAI / Groq / HF
      </footer>
    </div>
  );
}
