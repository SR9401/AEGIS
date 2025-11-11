// src/api/resources.js
import api from "./client";

export async function fetchResources({ page = 1, limit = 50, status } = {}) {
  const params = { page, limit };
  if (status) params.status = status;
  const { data } = await api.get("/resources", { params });
  // Supporte {items, total} ou liste brute selon ton back
  return Array.isArray(data) ? { items: data, total: data.length } : data;
}

export async function fetchAvailableResources() {
  const res = await fetchResources({ status: "available", limit: 200 });
  return res.items ?? res;
}

export async function createResource(payload) {
  // payload: { type, label, status?, details? }
  const { data } = await api.post("/resources", payload);
  return data;
}

export async function updateResource(id, payload) {
  const { data } = await api.patch(`/resources/${id}`, payload);
  return data;
}

export async function deleteResource(id) {
  const { data } = await api.delete(`/resources/${id}`);
  return data;
}