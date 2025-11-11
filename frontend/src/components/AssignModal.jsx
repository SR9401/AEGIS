// src/components/AssignModal.jsx
import { useEffect, useState } from "react";
import { fetchMissionsLite } from "../api/missions";
import { assignOne, assignMany } from "../api/assign";

export default function AssignModal({ resourceIds = [], onClose, onAssigned }) {
  const [missions, setMissions] = useState([]);
  const [missionId, setMissionId] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const isBulk = resourceIds.length > 1;

  useEffect(() => {
    let ok = true;
    (async () => {
      try {
        const lite = await fetchMissionsLite();
        if (ok) {
          setMissions(lite);
          if (lite[0]?.id) setMissionId(lite[0].id);
        }
      } finally { if (ok) setLoading(false); }
    })();
    return () => { ok = false; };
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      if (!missionId) throw new Error("Select a mission.");
      if (isBulk) {
        await assignMany(missionId, resourceIds, note || undefined);
      } else {
        await assignOne(missionId, resourceIds[0], note || undefined);
      }
      onAssigned?.();
      onClose?.();
    } catch (error) {
      const msg = error?.response?.data?.message || error?.message || "Assignment failed.";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-md bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">
            {isBulk ? `Assign ${resourceIds.length} resources` : "Assign resource"}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
        </div>

        {loading ? (
          <div className="text-slate-400">Loading…</div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-3">
            <div>
              <label className="text-sm text-slate-300">Mission</label>
              <select
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
                value={missionId} onChange={e=>setMissionId(e.target.value)}
              >
                {missions.map(m => <option key={m.id} value={m.id}>{m.title}</option>)}
              </select>
            </div>

            <div>
              <label className="text-sm text-slate-300">Note (optional)</label>
              <input
                className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
                value={note} onChange={e=>setNote(e.target.value)} placeholder="ex: Initial deployment"
              />
            </div>

            {err && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">{err}</div>}

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={onClose}
                className="px-4 py-2 rounded-xl border border-white/10 bg-slate-800/40 text-slate-200">Cancel</button>
              <button type="submit" disabled={loading}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-60">
                {loading ? "Assigning…" : "Assign"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
