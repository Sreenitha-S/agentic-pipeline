import { useState } from "react";

const STEP_META = {
  retrieve: { label: "Retrieve KB", cls: "kb" },
  route_decision: { label: "Route decision", cls: "reason" },
  tool_call: { label: "Tool call", cls: "tool" },
  synthesize_answer: { label: "Synthesize", cls: "reason" },
};

function stepLatency(step) {
  return typeof step.latency_ms === "number" ? step.latency_ms : 0;
}

export default function Waterfall({ trace, totalLatencyMs }) {
  const [openIdx, setOpenIdx] = useState(null);

  const maxLatency = Math.max(totalLatencyMs || 0, ...trace.map(stepLatency), 1);

  return (
    <div className="waterfall">
      <div className="waterfall-head">
        <span>Step</span>
        <span>Timing</span>
        <span className="waterfall-head-ms">ms</span>
      </div>

      {trace.map((step, idx) => {
        const meta = STEP_META[step.step] || { label: step.step, cls: "reason" };
        const skipped = step.skipped;
        const latency = stepLatency(step);
        const widthPct = skipped ? 0 : Math.max((latency / maxLatency) * 100, latency > 0 ? 1.5 : 0);
        const isOpen = openIdx === idx;

        return (
          <div className={`waterfall-row ${skipped ? "waterfall-row--skipped" : ""}`} key={idx}>
            <button
              className="waterfall-row-main"
              onClick={() => setOpenIdx(isOpen ? null : idx)}
              aria-expanded={isOpen}
            >
              <span className="waterfall-step-label">
                <span className={`dot dot--${meta.cls}`} />
                {meta.label}
              </span>

              <span className="waterfall-bar-track">
                {skipped ? (
                  <span className="waterfall-skipped-text">skipped &mdash; router decided KB was sufficient</span>
                ) : (
                  <span className={`waterfall-bar waterfall-bar--${meta.cls}`} style={{ width: `${widthPct}%` }} />
                )}
              </span>

              <span className="waterfall-ms">{skipped ? "\u2013" : latency}</span>
              <span className="waterfall-chevron">{isOpen ? "\u2212" : "+"}</span>
            </button>

            {isOpen && (
              <pre className="waterfall-detail">
                {JSON.stringify(
                  Object.fromEntries(Object.entries(step).filter(([k]) => k !== "step")),
                  null,
                  2
                )}
              </pre>
            )}
          </div>
        );
      })}

      <div className="waterfall-total">
        <span>Total end-to-end latency</span>
        <span className="waterfall-total-ms">{totalLatencyMs} ms</span>
      </div>
    </div>
  );
}
