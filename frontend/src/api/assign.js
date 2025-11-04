import api from "./client";

// Assigner UNE ressource à UNE mission
export async function assignResource({ mission_id, resource_id, note = null }) {
  const { data } = await api.post("/assign", { mission_id, resource_id, note });
  return data;
}