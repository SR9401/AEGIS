import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000" });

// inject token from localStorage if present
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});
export default api;
