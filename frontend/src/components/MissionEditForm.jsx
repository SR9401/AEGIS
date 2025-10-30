import { useState } from "react";
import { updateMission } from "../api/missions";

const statuses = [
  { value: "planned", label: "Planned" },
  { value: "active",  label: "Active"  },
  { value: "done",    label: "Done"    },
];

function toLocalDatetimeValue(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const pad = (n)=> String(n).padStart(2,"0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function MissionEditForm({ mission, onUpdated, onClose }) {
  const [title, setTitle] = useState(mission?.title ?? "");
  const [description, setDescription] = useState(mission?.description ?? "");
  const [status, setStatus] = useState(mission?.status ?? "planned");
  const [dateLocal, setDateLocal] = useState(toLocalDatetimeValue(mission?.date));
  const [lat, setLat] = useState(mission?.lat ?? "");
  const [lon, setLon] = useState(mission?.lon ?? "");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const patch = {
        title,
        description: description || null,
        status,
        dateLocal: dateLocal || null,
        lat: lat === "" ? null : Number(lat),
        lon: lon === "" ? null : Number(lon),
      };
      const updated = await updateMission(mission.id, patch);
      onUpdated?.(updated);
      onClose?.();
    } catch (error) {
      setErr(error?.response?.data?.message || "Update failed.");
    } finally { setLoading(false); }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-xl bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Edit Mission</h3>
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
                type="number" step="0.50" value={lat} onChange={e=>setLat(e.target.value)} />
            </div>
            <div>
              <label className="text-sm text-slate-300">Longitude</label>
              <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100 outline-none"
                type="number" step="0.50" value={lon} onChange={e=>setLon(e.target.value)} />
            </div>
          </div>

          {err && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">{err}</div>}

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-red-600 text-slate-200">Cancel</button>
            <button type="submit" disabled={loading}
              className="px-4 py-2 rounded-xl border border-white/10 hover:bg-blue-600 text-white font-medium disabled:opacity-60">
              {loading ? "Saving…" : "Save changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
