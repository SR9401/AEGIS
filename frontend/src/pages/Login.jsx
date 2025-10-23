import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosInstance";

/**
 * Page de connexion.
 * - POST /auth/login avec { email, password }
 * - stocke token dans localStorage et met header Authorization sur l'axios instance
 * - redirige vers "/"
 */
export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const validate = () => {
    const e = (email || "").trim().toLowerCase();
    if (!e || !e.includes("@")) {
      setError("Email invalide.");
      return false;
    }
    if (!password || password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères.");
      return false;
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.post("/auth/login", { email: email.trim().toLowerCase(), password });
      const token = res.data?.access_token ?? res.data?.token;
      const user = res.data?.user ?? null;

      if (!token) {
        setError("Réponse API invalide (token manquant).");
        return;
      }

      localStorage.setItem("access_token", token);
      if (user) localStorage.setItem("current_user", JSON.stringify(user));

      api.defaults.headers = api.defaults.headers || {};
      api.defaults.headers.common = api.defaults.headers.common || {};
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      // rediriger vers la home
      navigate("/", { replace: true });
    } catch (err) {
      console.error("login error:", err);
      if (err?.response?.status === 401) setError("Identifiants invalides.");
      else setError("Erreur lors de la connexion. Réessaye plus tard.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#071122" }}>
      <form onSubmit={handleSubmit} style={{ width: 420, padding: 24, borderRadius: 8, background: "#0b1a2a", color: "white", boxShadow: "0 6px 18px rgba(0,0,0,0.6)" }}>
        <h2 style={{ marginTop: 0, marginBottom: 12 }}>Se connecter — AEGIS</h2>

        {error && <div style={{ marginBottom: 12, color: "#ff8b8b" }}>{error}</div>}

        <label style={{ display: "block", marginBottom: 8 }}>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: "100%", padding: 10, marginTop: 6, borderRadius: 6, border: "1px solid rgba(255,255,255,0.06)", background: "#071b30", color: "white" }}
            required
          />
        </label>

        <label style={{ display: "block", marginBottom: 12 }}>
          Mot de passe
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", padding: 10, marginTop: 6, borderRadius: 6, border: "1px solid rgba(255,255,255,0.06)", background: "#071b30", color: "white" }}
            required
          />
        </label>

        <button type="submit" disabled={loading} style={{ width: "100%", padding: 10, borderRadius: 6, background: "#1f73ff", color: "white", border: "none", cursor: loading ? "default" : "pointer" }}>
          {loading ? "Connexion…" : "Se connecter"}
        </button>

        <div style={{ marginTop: 12, color: "#9fb2d8", fontSize: 13 }}>
          Pour la démo : utilises un utilisateur créé dans ta DB (curl POST /auth/login).
        </div>
      </form>
    </div>
  );
}
