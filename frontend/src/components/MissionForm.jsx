import { useState } from "react";
import { createMission } from "../api/missions";

const statuses = [
  { value: "planned", label: "Planned" },
  { value: "active",  label: "Active"  },
  { value: "done",    label: "Done"    },
];

export default function MissionForm({ onCreated, onClose }) {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("planned");
  const [dateLocal, setDateLocal] = useState("");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const payload = {
        title,
        description: description || null,
        status,
        dateLocal,
        lat: lat === "" ? null : Number(lat),
        lon: lon === "" ? null : Number(lon),
        created_by: user?.id,
      };
      const created = await createMission(payload);
      onCreated?.(created);
      onClose?.();
    } catch (error) {
      setErr(error?.response?.data?.message || "Creation failed.");
    } finally { setLoading(false); }
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
            <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
              value={title} onChange={e=>setTitle(e.target.value)} required />
          </div>

          <div>
            <label className="text-sm text-slate-300">Description</label>
            <textarea className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
              rows={3} value={description} onChange={e=>setDescription(e.target.value)} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="text-sm text-slate-300">Status</label>
              <select className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                value={status} onChange={e=>setStatus(e.target.value)}>
                {statuses.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="text-sm text-slate-300">Date & Time</label>
              <input type="datetime-local"
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                value={dateLocal} onChange={e=>setDateLocal(e.target.value)} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-slate-300">Latitude</label>
              <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                type="number" step="0.50" placeholder="44.843"
                value={lat} onChange={e=>setLat(e.target.value)} />
            </div>
            <div>
              <label className="text-sm text-slate-300">Longitude</label>
              <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                type="number" step="0.50" placeholder="-0.555"
                value={lon} onChange={e=>setLon(e.target.value)} />
            </div>
          </div>

          {err && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">{err}</div>}

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-red-600 text-slate-200">Cancel</button>
            <button type="submit" disabled={loading}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-blue-600 text-white font-medium disabled:opacity-60">
              {loading ? "Creating…" : "Create Mission"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
