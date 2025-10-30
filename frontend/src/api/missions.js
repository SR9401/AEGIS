import api from "./client";

export async function fetchMissions(params = {}) {
  const { data } = await api.get("/missions", { params });
  return Array.isArray(data) ? data : (data.items || []);
}

export async function createMission(payload) {
  // backend attend date en ISO, status parmi planned|active|done
  const { dateLocal, ...rest } = payload;
  const iso = dateLocal ? new Date(dateLocal).toISOString() : null;
  const body = { ...rest, date: iso };
  const { data } = await api.post("/missions", body);
  return data;
}

export async function updateMission(id, patch) {
  const p = { ...patch };
  if (p.dateLocal) {
    p.date = new Date(p.dateLocal).toISOString();
    delete p.dateLocal;
  }
  const { data } = await api.patch(`/missions/${id}`, p);
  return data;
}

export async function deleteMission(id) {
  await api.delete(`/missions/${id}`);
}
