import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { fetchResources, deleteResource } from "../api/resources";
import ResourceForm from "../components/ResourceForm";

function Row({ r, onDelete }) {
  const pill =
    r.status === "available"   ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/20" :
    r.status === "maintenance" ? "bg-amber-500/20 text-amber-300 border-amber-400/20" :
                                 "bg-slate-500/20 text-slate-300 border-slate-400/20";
  return (
    <div className="flex items-center justify-between bg-slate-900/60 border border-white/10 rounded-xl p-4">
      <div>
        <div className="text-white font-medium">{r.label}</div>
        <div className="text-slate-400 text-sm">{r.type} • {r.details || "—"}</div>
      </div>
      <div className="flex items-center gap-3">
        <span className={`text-[11px] px-2 py-1 rounded-lg border ${pill}`}>{r.status}</span>
        <button onClick={()=>onDelete(r.id)} className="px-3 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white">Delete</button>
      </div>
    </div>
  );
}

export default function ResourcesPage() {
  const [items, setItems] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  async function load() {
    setErr(""); setLoading(true);
    try {
      const data = await fetchResources({ page:1, limit:50 });
      setItems(data);
    } catch (e) {
      setErr(e?.response?.data?.message || "Failed to load resources.");
    } finally { setLoading(false); }
  }

  useEffect(()=>{ load(); }, []);

  async function onDelete(id) {
    if (!confirm("Delete this resource?")) return;
    await deleteResource(id);
    setItems(prev => prev.filter(x => x.id !== id));
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Topbar />
        <div className="p-4 md:p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold">Resources</h2>
              <p className="text-slate-400 text-sm">Manage operational assets</p>
            </div>
            <button onClick={()=>setShowForm(true)}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
              + New Resource
            </button>
          </div>

          {err && <div className="mb-3 text-sm text-red-400">{err}</div>}

          {loading ? (
            <div className="text-slate-400">Loading…</div>
          ) : items.length === 0 ? (
            <div className="text-slate-400">No resources yet.</div>
          ) : (
            <div className="space-y-3">
              {items.map(r => <Row key={r.id} r={r} onDelete={onDelete} />)}
            </div>
          )}
        </div>
      </main>

      {showForm && (
        <ResourceForm
          onCreated={(r)=> setItems(prev => [r, ...prev])}
          onClose={()=> setShowForm(false)}
        />
      )}
    </div>
  );
}
