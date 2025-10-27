import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000" });

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("access_token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login"; // redirige
    }
    return Promise.reject(err);
  }
);

export default api;
