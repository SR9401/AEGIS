import { NavLink } from "react-router-dom";

const linkBase = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium";
const active = "bg-blue-600 text-white border border-white/10";
const idle   = "text-slate-300 hover:bg-blue-800 hover:text-white";

export default function Sidebar() {
  return (
    <aside className="w-56 bg-slate-900/80 border-r border-white/10 p-3 flex flex-col">
      <div className="flex items-center gap-2 px-2 py-3">
		        {/* Icon */}
		<div className="flex justify-center mb-6">
		<div className="w-22 h-22 rounded-2xl bg-[#0F182D] border border-indigo-400/30 flex items-center justify-center overflow-hidden">
			<img
			src="img/logo-aegis.png"
			alt="AEGIS"
			className="w-22 h-22 object-contain"
			draggable="false"
			/>
		</div>
		</div>
        <div>
          <h1 className='font-["Cinzel",serif] text-3xl tracking-wider'>AEGIS</h1>
          <div className="text-[10px] text-slate-400">v2.1.0</div>
        </div>
      </div>

      <nav className="mt-2 space-y-1">
        <NavLink to="/dashboard" className={({isActive}) => `${linkBase} ${isActive?active:idle}`}>Dashboard</NavLink>
        <NavLink to="/missions"  className={({isActive}) => `${linkBase} ${isActive?active:idle}`}>Missions</NavLink>
        <NavLink to="/resources" className={({isActive}) => `${linkBase} ${isActive?active:idle}`}>Resources</NavLink>
        <NavLink to="/users"     className={({isActive}) => `${linkBase} ${isActive?active:idle}`}>Personnel</NavLink>
      </nav>

      <div className="mt-auto text-[11px] text-slate-500 space-y-1">
        <div className="flex items-center justify-between px-2">
          <span>System Status</span><span className="text-green-400">● ONLINE</span>
        </div>
        <div className="flex items-center justify-between px-2">
          <span>Security Level</span><span className="text-amber-400">ELEVATED</span>
        </div>
      </div>
    </aside>
  );
}
