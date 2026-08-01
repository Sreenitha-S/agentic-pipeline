const EXAMPLES = [
  { label: "Team plan price?", value: "How much does the Team plan cost per month?", kind: "tool" },
  { label: "Data encrypted?", value: "Is my data encrypted at rest?", kind: "kb" },
  { label: "Business API quota?", value: "How many API calls does the Business plan include per month?", kind: "tool" },
  { label: "Sharing controls?", value: "Can I restrict external sharing for my whole organization?", kind: "kb" },
];

export default function QueryForm({
  question,
  setQuestion,
  routerVersion,
  setRouterVersion,
  retrieverKind,
  setRetrieverKind,
  onSubmit,
  loading,
}) {
  function handleSubmit(e) {
    e.preventDefault();
    if (!loading && question.trim()) onSubmit();
  }

  return (
    <form className="query-form" onSubmit={handleSubmit}>
      <label className="query-label" htmlFor="question-input">Ask CloudNest support</label>
      <div className="query-input-row">
        <input
          id="question-input"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. How much does the Team plan cost per month?"
          autoComplete="off"
        />
        <button type="submit" className="run-btn" disabled={loading || !question.trim()}>
          {loading ? "Running\u2026" : "Run"}
        </button>
      </div>

      <div className="example-chips">
        <span className="example-label">Try:</span>
        {EXAMPLES.map((ex) => (
          <button
            type="button"
            key={ex.value}
            className={`chip chip--${ex.kind}`}
            onClick={() => setQuestion(ex.value)}
          >
            {ex.label}
          </button>
        ))}
      </div>

      <div className="control-row">
        <div className="control-group">
          <span className="control-label">Router prompt</span>
          <div className="segmented">
            {["v1", "v2"].map((v) => (
              <button
                type="button"
                key={v}
                className={routerVersion === v ? "segmented-btn active" : "segmented-btn"}
                onClick={() => setRouterVersion(v)}
              >
                {v}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group">
          <span className="control-label">Retriever</span>
          <div className="segmented">
            {[
              { key: "tfidf", label: "TF-IDF" },
              { key: "embeddings", label: "Embeddings" },
            ].map((r) => (
              <button
                type="button"
                key={r.key}
                className={retrieverKind === r.key ? "segmented-btn active" : "segmented-btn"}
                onClick={() => setRetrieverKind(r.key)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </form>
  );
}
