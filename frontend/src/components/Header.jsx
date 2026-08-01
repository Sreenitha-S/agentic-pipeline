export default function Header({ providerInfo, backendReachable }) {
  const provider = providerInfo?.provider;
  const isMock = providerInfo?.is_mock;

  return (
    <header className="header">
      <div className="header-title">
        <span className="header-mark" aria-hidden="true" />
        <div>
          <h1>CloudNest Agent Console</h1>
          <p className="header-sub">retriever &rarr; router &rarr; tool &rarr; synthesis, traced live</p>
        </div>
      </div>

      <div className="header-status">
        {!backendReachable ? (
          <span className="status-pill status-pill--danger">
            <span className="status-dot status-dot--danger" />
            backend unreachable
          </span>
        ) : (
          <span className={`status-pill ${isMock ? "status-pill--warn" : "status-pill--live"}`}>
            <span className={`status-dot ${isMock ? "status-dot--warn" : "status-dot--live"}`} />
            {provider || "checking..."}
          </span>
        )}
      </div>
    </header>
  );
}
