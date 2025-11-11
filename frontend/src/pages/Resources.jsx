// src/pages/Resources.jsx
import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { fetchResources, deleteResource } from "../api/resources";
import ResourceEditModal from "../components/ResourceEditModal";
import AssignModal from "../components/AssignModal";
import ResourceCreateModal from "../components/ResourceCreateModal";

export default function ResourcesPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const [editItem, setEditItem] = useState(null);
  const [assignIds, setAssignIds] = useState(null); // array de resourceIds (single ou bulk)
  const [selected, setSelected] = useState([]);     // pour bulk assign
  const [openCreate, setOpenCreate] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await fetchResources({ page: 1, limit: 200 });
      setItems(res.items ?? res);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function toggleSelect(id) {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Topbar />

        <div className="p-4 md:p-6 space-y-4">
          {/* Header actions */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Resources</h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setOpenCreate(true)}
                className="px-3 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500"
              >
                New Resource
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="bg-slate-900/60 border border-white/10 rounded-xl overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/70 text-slate-300">
                <tr>
                  <th className="px-4 py-3 w-10"></th>
                  <th className="px-4 py-3">Label</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Details</th>
                  <th className="px-4 py-3 w-56">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {loading ? (
                  <tr>
                    <td className="px-4 py-4 text-slate-400" colSpan={6}>Loading…</td>
                  </tr>
                ) : items.length === 0 ? (
                  <tr>
                    <td className="px-4 py-4 text-slate-400" colSpan={6}>No resources.</td>
                  </tr>
                ) : (
                  items.map((r) => {
                    const isAssigned = String(r.status).toLowerCase() === "assigned";
                    return (
                      <tr key={r.id} className="hover:bg-slate-800/30">
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selected.includes(r.id)}
                            onChange={() => toggleSelect(r.id)}
                          />
                        </td>
                        <td className="px-4 py-3">{r.label}</td>
                        <td className="px-4 py-3 text-slate-300">{r.type}</td>
                        <td className="px-4 py-3 text-slate-400">{r.status}</td>
                        <td className="px-4 py-3 text-slate-400">{r.details || "—"}</td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <button
                              className="px-3 py-1.5 rounded-lg border border-white/10 bg-slate-800/40 hover:bg-slate-800"
                              onClick={() => setEditItem(r)}
                            >
                              Edit
                            </button>
                            <button
                              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500"
                              onClick={() => setAssignIds([r.id])}
                            >
                              Assign
                            </button>
                            <button
                              className="px-3 py-1.5 rounded-lg border border-red-500/30 text-red-300 bg-red-500/10 hover:bg-red-500/20 disabled:opacity-60"
                              onClick={async () => {
                                if (!confirm(`Delete resource "${r.label}" ?`)) return;
                                try {
                                  await deleteResource(r.id);
                                  await load();
                                } catch (e) {
                                  const msg = e?.response?.data?.message || "Delete failed.";
                                  alert(msg);
                                }
                              }}
                              disabled={isAssigned}
                              title={isAssigned ? "Unassign it from missions first" : ""}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Modals */}
      {editItem && (
        <ResourceEditModal
          resource={editItem}
          onClose={() => setEditItem(null)}
          onSaved={() => { setEditItem(null); load(); }}
        />
      )}

      {assignIds && (
        <AssignModal
          resourceIds={assignIds}
          onClose={() => setAssignIds(null)}
          onAssigned={() => { setAssignIds(null); load(); }}
        />
      )}

      {openCreate && (
        <ResourceCreateModal
          onClose={() => setOpenCreate(false)}
          onCreated={() => { setOpenCreate(false); load(); }}
        />
      )}
    </div>
  );
}
