export default function RetrievalHits({ hits }) {
  if (!hits || hits.length === 0) return null;
  const maxScore = Math.max(...hits.map((h) => h.score), 0.0001);

  return (
    <div className="hits">
      <span className="hits-label">Retrieved passages</span>
      <div className="hits-list">
        {hits.map((h) => (
          <div className="hit" key={h.doc_id}>
            <span className="hit-name">{h.doc_id}</span>
            <span className="hit-bar-track">
              <span className="hit-bar" style={{ width: `${(h.score / maxScore) * 100}%` }} />
            </span>
            <span className="hit-score">{h.score.toFixed(3)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
