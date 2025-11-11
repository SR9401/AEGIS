import { useEffect, useState } from "react";
import { createMission } from "../api/missions";
import { fetchAvailableResources } from "../api/resources";
import { assignMany } from "../api/assign";

const statuses = [
  { value: "planned", label: "Planned" },
  { value: "active",  label: "Active"  },
  { value: "done",    label: "Done"    },
];

export default function MissionForm({ onCreated, onClose }) {
  // Champs mission
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("planned");
  const [dateLocal, setDateLocal] = useState("");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");

  // Ressources
  const [resources, setResources] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  // Charger les ressources disponibles
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetchAvailableResources();
        // Supporte les 2 formats: {items:[...]} OU [...]
        const list = Array.isArray(res) ? res : Array.isArray(res?.items) ? res.items : [];
        if (alive) setResources(list);
      } catch (e) {
        // On n'empêche pas la création si la liste échoue
        console.warn("Failed to load available resources", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      // 1) Construire la payload mission (le backend attend "date" en ISO)
      const payload = {
        title: title.trim(),
        description: (description || "").trim() || null,
        status,
        date: dateLocal ? new Date(dateLocal).toISOString() : null,
        lat: lat === "" ? null : Number(lat),
        lon: lon === "" ? null : Number(lon),
        // created_by: laissé au backend via JWT (g.user_id)
      };

      // Sanity check basique
      if (!payload.title) {
        throw new Error("Title is required.");
      }
      if ((payload.lat !== null && Number.isNaN(payload.lat)) ||
          (payload.lon !== null && Number.isNaN(payload.lon))) {
        throw new Error("Latitude/Longitude must be numbers.");
      }

      // 2) Créer la mission
      const created = await createMission(payload);

      // 3) Assigner en bulk les ressources sélectionnées (optionnel)
      if (selectedIds.length > 0) {
        const { data, status: httpStatus } = await assignMany(created.id, selectedIds, "Assigned at creation");
        if (httpStatus === 207 && data?.errors?.length) {
          console.warn("Partial assignment errors:", data.errors);
        }
      }

      onCreated?.(created);
      onClose?.();
    } catch (error) {
      const apiMsg =
        error?.response?.data?.message ||
        error?.message ||
        "Creation failed.";
      setErr(apiMsg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-xl bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">New Mission</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-slate-300">Title</label>
            <input
              className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
              value={title}
              onChange={(e)=>setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-sm text-slate-300">Description</label>
            <textarea
              className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
              rows={3}
              value={description}
              onChange={(e)=>setDescription(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="text-sm text-slate-300">Status</label>
              <select
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                value={status}
                onChange={(e)=>setStatus(e.target.value)}
              >
                {statuses.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="text-sm text-slate-300">Date & Time</label>
              <input
                type="datetime-local"
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                value={dateLocal}
                onChange={(e)=>setDateLocal(e.target.value)}
              />
            </div>
          </div>

          {/* Sélecteur multi-ressources */}
          <div>
            <label className="text-sm text-slate-300">Assign Resources (optional)</label>
            <select
              multiple
              className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none h-32"
              value={selectedIds}
              onChange={(e) => {
                const vals = Array.from(e.target.selectedOptions).map(o => o.value);
                setSelectedIds(vals);
              }}
            >
              {resources.map(r => (
                <option key={r.id} value={r.id}>
                  {r.label} — {r.type}
                </option>
              ))}
            </select>
            <p className="text-[12px] text-slate-500 mt-1">
              Maintiens Ctrl/Cmd pour multi-sélectionner.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-slate-300">Latitude</label>
              <input
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                type="number" step="0.0001" placeholder="44.843"
                value={lat}
                onChange={(e)=>setLat(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm text-slate-300">Longitude</label>
              <input
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                type="number" step="0.0001" placeholder="-0.555"
                value={lon}
                onChange={(e)=>setLon(e.target.value)}
              />
            </div>
          </div>

          {err && (
            <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">
              {err}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl border border-white/10 bg-slate-800/40 text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium disabled:opacity-60"
            >
              {loading ? "Creating…" : "Create Mission"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
