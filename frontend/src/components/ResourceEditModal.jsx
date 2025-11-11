// src/components/ResourceEditModal.jsx
import { useState } from "react";
import { updateResource } from "../api/resources";

const statuses = [
  { value: "available",   label: "Available" },
  { value: "assigned",    label: "Assigned" },
  { value: "maintenance", label: "Maintenance" },
];

export default function ResourceEditModal({ resource, onClose, onSaved }) {
  const [type, setType] = useState(resource?.type || "");
  const [label, setLabel] = useState(resource?.label || "");
  const [status, setStatus] = useState(resource?.status || "available");
  const [details, setDetails] = useState(resource?.details || "");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setErr(""); setSaving(true);
    try {
      const payload = {
        type: type.trim(),
        label: label.trim(),
        status,
        details: details.trim() || null,
      };
      await updateResource(resource.id, payload);
      onSaved?.();
      onClose?.();
    } catch (error) {
      const msg = error?.response?.data?.message || "Update failed.";
      setErr(msg);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-lg bg-slate-900 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Edit Resource</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
        </div>

        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label className="text-sm text-slate-300">Label</label>
            <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
              value={label} onChange={e=>setLabel(e.target.value)} required />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-slate-300">Type</label>
              <input className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
                value={type} onChange={e=>setType(e.target.value)} required />
            </div>
            <div>
              <label className="text-sm text-slate-300">Status</label>
              <select className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
                value={status} onChange={e=>setStatus(e.target.value)}>
                {statuses.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="text-sm text-slate-300">Details</label>
            <textarea className="mt-1 w-full bg-slate-800/60 border border-white/10 rounded-xl px-3 py-2 text-slate-100"
              rows={3} value={details} onChange={e=>setDetails(e.target.value)} />
          </div>

          {err && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-3 py-2">{err}</div>}

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="px-4 py-2 rounded-xl border border-white/10 bg-slate-800/40 text-slate-200">Cancel</button>
            <button type="submit" disabled={saving}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-60">
              {saving ? "Saving…" : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
