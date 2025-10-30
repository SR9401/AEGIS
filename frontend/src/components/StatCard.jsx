export function StatCard({ title, value, subtitle }) {
  return (
    <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
      <div className="text-slate-300 text-sm">{title}</div>
      <div className="text-2xl font-semibold text-white mt-1">{value}</div>
      {subtitle && <div className="text-[11px] text-slate-500 mt-1">{subtitle}</div>}
    </div>
  );
}
