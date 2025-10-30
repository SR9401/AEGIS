function Progress({ value=0 }) {
  return (
    <div className="w-full h-1.5 bg-slate-800/60 rounded-full overflow-hidden">
      <div className="h-full bg-indigo-500" style={{width: `${Math.min(100, Math.max(0, value))}%`}} />
    </div>
  );
}

export default function OperationCard({ m }) {
  const statusColor = {
    planned:  "bg-yellow-500/20 text-yellow-300 border-yellow-400/30",
    active:   "bg-green-500/20 text-green-300 border-green-400/30",
    done:     "bg-slate-500/20 text-slate-300 border-slate-400/30",
  }[m.status] || "bg-slate-500/20 text-slate-300 border-slate-400/30";

  const p = m.status === "done" ? 100 : m.status === "active" ? 65 : 25;

  return (
    <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`px-2 py-0.5 text-[11px] rounded-lg border ${statusColor}`}>{m.status}</div>
          <div className="text-white font-medium">{m.title}</div>
        </div>
        <div className="text-slate-500 text-xs">›</div>
      </div>
      <div className="text-slate-400 text-sm mt-1 line-clamp-2">{m.description || "—"}</div>
      <div className="mt-3"><Progress value={p} /></div>
      <div className="mt-2 text-[12px] text-slate-500 flex gap-4">
        {m.date && <span>🗓️ {m.date?.slice(0,16)}</span>}
        {(m.lat!=null && m.lon!=null) && <span>📍 {m.lat.toFixed?.(2) ?? m.lat}, {m.lon.toFixed?.(2) ?? m.lon}</span>}
      </div>
    </div>
  );
}
