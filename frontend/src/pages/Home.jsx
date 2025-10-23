import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import DashboardCards from "../components/DashboardCards";
import MissionsList from "../components/MissionsList";
import api from "../api/axiosInstance";

/**
 * Page d'accueil / dashboard.
 * - récupère la liste des missions via GET /missions
 * - redirige vers /login si 401
 * - passe missions/loading aux composants enfants
 */
export default function Home() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;

    async function fetchMissions() {
      setLoading(true);
      setError(null);
      try {
		const res = await api.get("/missions");

		let data = [];
		if (Array.isArray(res.data)) {
			data = res.data;
		} else if (Array.isArray(res.data.items)) {
			data = res.data.items;
		} else if (Array.isArray(res.data.missions)) {
			data = res.data.missions;
		} else {
			console.warn("Shape inattendue pour /missions:", res.data);
		}

		if (mounted) setMissions(data);

      } catch (err) {
        // Si l'API répond 401 -> renvoyer vers login
        if (err?.response?.status === 401) {
          try { localStorage.removeItem("access_token"); } catch (_) {}
          navigate("/login", { replace: true });
          return;
        }
        console.error("fetch missions error:", err);
        if (mounted) setError("Impossible de charger les missions.");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchMissions();
    return () => { mounted = false; };
  }, [navigate]);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#081427", color: "white" }}>
      <Sidebar />
      <main style={{ flex: 1, padding: 20 }}>
        <Topbar />
        <section style={{ marginTop: 20 }}>
          {error && (
            <div style={{ marginBottom: 12, color: "#ffb4b4" }}>
              {error} <button onClick={() => window.location.reload()}>Réessayer</button>
            </div>
          )}
          <DashboardCards missions={missions} loading={loading} />
          <div style={{ marginTop: 18 }}>
            <MissionsList missions={missions} loading={loading} />
          </div>
        </section>
      </main>
    </div>
  );
}
