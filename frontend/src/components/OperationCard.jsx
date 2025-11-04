function Progress({ value = 0 }) {
  const v = Math.min(100, Math.max(0, value));
  return (
    <div className="w-full h-1.5 bg-slate-800/60 rounded-full overflow-hidden">
      <div className="h-full bg-indigo-500" style={{ width: `${v}%` }} />
    </div>
  );
}

export default function OperationCard({ m, onSelect }) {
  const statusColor =
    {
      planned: "bg-yellow-500/20 text-yellow-300 border-yellow-400/30",
      active: "bg-green-500/20 text-green-300 border-green-400/30",
      done: "bg-slate-500/20 text-slate-300 border-slate-400/30",
    }[m.status] || "bg-slate-500/20 text-slate-300 border-slate-400/30";

  const progress = m.status === "done" ? 100 : m.status === "active" ? 65 : 25;

  // petite aide pour afficher la date lisible si c'est une string ISO
  const dateShort =
    typeof m.date === "string" ? m.date.slice(0, 16) : "";

  const latShort =
    m.lat != null ? (typeof m.lat === "number" ? m.lat.toFixed(2) : m.lat) : null;
  const lonShort =
    m.lon != null ? (typeof m.lon === "number" ? m.lon.toFixed(2) : m.lon) : null;

  return (
    <div
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect?.()}
      className="cursor-pointer bg-slate-900/60 border border-white/10 rounded-xl p-4 hover:border-white/20 transition"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <div className={`px-2 py-0.5 text-[11px] rounded-lg border shrink-0 ${statusColor}`}>
            {m.status}
          </div>
          <div className="text-white font-medium truncate">{m.title}</div>
        </div>
        <div className="text-slate-500 text-xs">›</div>
      </div>

      <div className="text-slate-400 text-sm mt-1 line-clamp-2">
        {m.description || "—"}
      </div>

      <div className="mt-3">
        <Progress value={progress} />
      </div>

      <div className="mt-2 text-[12px] text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
        {dateShort && <span>🗓️ {dateShort}</span>}
        {latShort != null && lonShort != null && <span>📍 {latShort}, {lonShort}</span>}
      </div>
    </div>
  );
}
