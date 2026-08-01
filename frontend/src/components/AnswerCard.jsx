export default function AnswerCard({ state }) {
  if (!state) return null;

  const decision = state.router_decision;
  const usedTool = decision?.use_tool;

  return (
    <div className="answer-card">
      <div className="answer-card-eyebrow">
        <span className={`badge ${usedTool ? "badge--tool" : "badge--kb"}`}>
          {usedTool ? `tool: pricing_lookup(${decision.tool_query})` : "answered from KB"}
        </span>
        <span className="answer-meta">retriever: {state.retriever_kind}</span>
      </div>
      <p className="answer-text">{state.answer}</p>
      {decision?.reason && <p className="answer-reason">&ldquo;{decision.reason}&rdquo;</p>}
    </div>
  );
}
