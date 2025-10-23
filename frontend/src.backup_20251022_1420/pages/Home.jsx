import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import DashboardCards from "../components/DashboardCards";
import MissionsList from "../components/MissionsList";
import api from "../api/axiosInstance";


export default function Home() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function fetchMissions() {
      try {
        const res = await api.get("/missions");
        if (!cancelled) setMissions(res.data || []);
      } catch (err) {
        console.error("fetch missions", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchMissions();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-r from-[#07103a] via-[#0e2a6a] to-[#08307a] text-gray-200">
      <Sidebar />
      <div className="ml-72"> {/* largeur sidebar fixe */}
        <Topbar />
        <main className="px-6 py-8">
          <DashboardCards missions={missions} />
          <div className="mt-6 grid grid-cols-12 gap-6">
            <section className="col-span-8">
              <MissionsList missions={missions} loading={loading} />
            </section>
            <aside className="col-span-4 space-y-6">
              <MapWidget missions={missions} />
              <QuickActions />
            </aside>
          </div>
        </main>
      </div>
    </div>
  );
}
