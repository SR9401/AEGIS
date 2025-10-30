export default function Topbar() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return (
    <header className="h-14 border-b border-white/10 px-4 flex items-center justify-between bg-slate-900/60">
      <input
        type="text"
        placeholder="Search missions, personnel, resources…"
        className="w-[520px] bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 outline-none"
      />
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-400 hidden md:block">GMT {new Date().toUTCString().slice(0,16)}</span>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-indigo-500/30 border border-indigo-400/30" />
          <span className="text-slate-200">{user?.first_name || "Operator"}</span>
        </div>
      </div>
    </header>
  );
}
