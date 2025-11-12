// src/api/assign.js
import api from "./client";

// SINGLE assign: { resource_id, note? }
export async function assignOne(mid, resourceId, note) {
  const { data } = await api.post(`/missions/${mid}/assign`, {
    resource_id: resourceId,
    note: note || undefined,
  });
  return data;
}

// BULK assign: { resource_ids: [], note? } => 201 ou 207 (assigned[], errors[])
export async function assignMany(mid, resourceIds = [], note) {
  const { data, status } = await api.post(`/missions/${mid}/assign`, {
    resource_ids: resourceIds,
    note: note || undefined,
  });
  return { data, status }; // { assigned:[], errors:[] } si 207
}

// UNASSIGN (supprimer le lien)
export async function unassign(mid, linkId) {
  const { data } = await api.delete(`/missions/${mid}/assign/${linkId}`);
  return data; // {ok:true}
}
