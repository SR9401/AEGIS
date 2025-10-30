import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import MissionForm from "../components/MissionForm";
import { fetchMissions, deleteMission } from "../api/missions";
import MissionEditForm from "../components/MissionEditForm";

function MissionListItem({ m, onSelect }) {
  const bar =
    m.status === "active" ? "bg-blue-500" :
    m.status === "planned" ? "bg-amber-500" : "bg-slate-500";
  const pct = m.status === "done" ? 100 : m.status === "active" ? 65 : 0;

  return (
    <button onClick={()=>onSelect(m)}
      className="w-full text-left bg-slate-900/60 border border-white/10 rounded-xl p-4 hover:bg-slate-900">
      <div className="flex items-center justify-between">
        <div className="text-white font-medium">{m.title}</div>
        <span className="text-[11px] px-2 py-0.5 rounded-lg border border-white/10 text-slate-300">{m.status}</span>
      </div>
      <div className="text-slate-400 text-sm mt-1 line-clamp-2">{m.description || "—"}</div>
      <div className="mt-3 h-1.5 bg-slate-800/60 rounded-full overflow-hidden">
        <div className={`h-full ${bar}`} style={{width:`${pct}%`}} />
      </div>
      <div className="mt-2 text-[12px] text-slate-500 flex gap-4">
        {m.date && <span>🗓 {m.date.slice(0,16)}</span>}
        {(m.lat!=null && m.lon!=null) && <span>📍 {m.lat}, {m.lon}</span>}
      </div>
    </button>
  );
}

export default function MissionsPage() {
  const [missions, setMissions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [showEdit, setShowEdit] = useState(false);

function openEdit() { if (selected) setShowEdit(true); }

function applyUpdated(updated) {
  setMissions(prev => prev.map(m => (m.id === updated.id ? updated : m)));
  setSelected(updated);
}

  async function load() {
    setErr(""); setLoading(true);
    try {
      const data = await fetchMissions({ page:1, limit:20 });
      setMissions(data);
      if (data.length && !selected) setSelected(data[0]);
    } catch (e) {
      setErr(e?.response?.data?.message || "Failed to load missions.");
    } finally { setLoading(false); }
  }

  useEffect(()=>{ load();}, []);

  async function onDelete(id) {
    if (!confirm("Delete this mission?")) return;
    await deleteMission(id);
    setSelected(null);
    load();
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Topbar />

        <div className="p-4 md:p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold">Missions Management</h2>
              <p className="text-slate-400 text-sm">Plan, monitor, and manage all mission operations</p>
            </div>
            <button onClick={()=>setShowForm(true)}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
              + New Mission
            </button>
          </div>

          {err && <div className="mb-3 text-sm text-red-400">{err}</div>}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Liste */}
            <section className="space-y-3 lg:col-span-1">
              {loading ? (
                <div className="text-slate-400">Loading…</div>
              ) : missions.length === 0 ? (
                <div className="text-slate-400">No missions yet.</div>
              ) : (
                missions.map(m => (
                  <MissionListItem key={m.id} m={m} onSelect={setSelected} />
                ))
              )}
            </section>

            {/* Détails */}
            <section className="lg:col-span-2 space-y-4">
              {selected ? (
                <>
                  <div className="bg-slate-900/60 border border-white/10 rounded-xl p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold">{selected.title}</h3>
                        <p className="text-slate-400 mt-1">{selected.description || "—"}</p>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={openEdit}
  							className="px-3 py-2 rounded-xl border border-white/10 hover:bg-green-600 text-slate-200">
  							Edit
						</button>
                        <button onClick={()=>onDelete(selected.id)} className="px-3 py-2 rounded-xl border border-white/10 hover:bg-red-600 text-slate-200">Delete</button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4 text-sm">
                      <div className="bg-slate-900/60 border border-white/10 rounded-xl p-3">
                        <div className="text-slate-400">Status</div>
                        <div className="text-white">{selected.status}</div>
                      </div>
                      <div className="bg-slate-900/60 border border-white/10 rounded-xl p-3">
                        <div className="text-slate-400">Date</div>
                        <div className="text-white">{selected.date ? selected.date.slice(0,16) : "—"}</div>
                      </div>
                      <div className="bg-slate-900/60 border border-white/10 rounded-xl p-3">
                        <div className="text-slate-400">Location</div>
                        <div className="text-white">
                          {(selected.lat!=null && selected.lon!=null) ? `${selected.lat}, ${selected.lon}` : "—"}
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-slate-400">Select a mission to see details.</div>
              )}
            </section>
          </div>
        </div>
      </main>
		{showEdit && selected && (
		<MissionEditForm
			mission={selected}
			onUpdated={applyUpdated}
			onClose={()=>setShowEdit(false)}
		/>
		)}
      {showForm && (
        <MissionForm
          onCreated={(m)=>{ setMissions(prev=>[m, ...prev]); setSelected(m); }}
          onClose={()=>setShowForm(false)}
        />
      )}
    </div>
  );
}
