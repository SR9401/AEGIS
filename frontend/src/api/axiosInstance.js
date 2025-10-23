import axios from "axios";

/**
 * Pour Vite : utiliser import.meta.env.VITE_API_URL
 * Si non défini, on retombe sur http://127.0.0.1:5000 en dev.
 */
const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const api = axios.create({
  baseURL: BASE,
  timeout: 10000,
});

// Si un token est stocké localement, l'ajouter automatiquement
const token = localStorage.getItem("access_token");
if (token) {
  api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

// Intercepteur simple : redirect to /login on 401
api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    if (err?.response?.status === 401) {
      try { localStorage.removeItem("access_token"); } catch (_) {}
      // forcer la redirection
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
