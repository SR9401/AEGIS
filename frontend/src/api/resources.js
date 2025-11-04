import api from "./client";

export async function fetchResources(params = {}) {
  const { data } = await api.get("/resources", { params });
  return Array.isArray(data) ? data : (data.items || []);
}

export async function fetchAvailableResources() {
  const all = await fetchResources({ limit: 200 });
  return all.filter(r => r.status === "available");
}

export async function createResource(payload) {
  const body = {
    type: payload.type,
    label: payload.label,
    status: payload.status || "available",
    details: payload.details || null,
  };
  const { data } = await api.post("/resources", body);
  return data;
}

export async function deleteResource(id) {
  await api.delete(`/resources/${id}`);
}
