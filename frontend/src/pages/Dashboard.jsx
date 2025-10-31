import { useEffect, useState, useMemo } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { StatCard } from "../components/StatCard";
import OperationCard from "../components/OperationCard";
import { fetchMissions } from "../api/missions";
import MapView from "../components/MapView";

export default function Dashboard() {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await fetchMissions({ page: 1, limit: 10 });
        if (mounted) setMissions(data);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const stats = useMemo(() => {
    const total = missions.length;
    const active = missions.filter((m) => m.status === "active").length;
    const done = missions.filter((m) => m.status === "done").length;
    const critical = missions.filter((m) =>
      /critical|urgent/i.test(m.description || "")
    ).length;
    return { total, active, done, critical };
  }, [missions]);

  const [selected, setSelected] = useState(null);
  function handleMarkerClick(m) {
    setSelected(m);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <Topbar />

        <div className="p-4 md:p-6 space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard title="Active Missions" value={stats.active} subtitle="Currently in progress" />
            <StatCard title="Critical Operations" value={stats.critical} subtitle="Requiring attention" />
            <StatCard title="Completed" value={stats.done} subtitle="Successfully finished" />
            <StatCard title="Total Missions" value={stats.total} subtitle="All time" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Active Operations */}
            <section className="lg:col-span-2 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Active Operations</h3>
                <div className="text-[12px] text-slate-400">{missions.length} Total</div>
              </div>

              {loading ? (
                <div className="text-slate-400">Loading missions…</div>
              ) : missions.length === 0 ? (
                <div className="text-slate-400">No missions yet.</div>
              ) : (
                missions.map((m) => <OperationCard key={m.id} m={m} />)
              )}
            </section>

            {/* Right column: Weather • Overview • Map • Quick Actions */}
            <section className="space-y-4">
              <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
                <div className="text-slate-300 text-sm mb-2">Weather Conditions</div>
                <div className="text-3xl font-semibold">72°F</div>
                <div className="text-slate-400 text-sm">Partly Cloudy</div>
                <div className="text-[12px] text-slate-500 mt-2">Wind 12 mph • Humidity 65%</div>
              </div>

              <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
                <div className="text-slate-300 text-sm mb-2">Mission Overview</div>
                <div className="h-40 rounded-lg bg-slate-800/40 border border-white/10 flex items-center justify-center text-slate-500">
                  (Chart placeholder)
                </div>
                <div className="mt-2 text-[12px] text-slate-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Active Missions</span><span>{stats.active}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Critical Operations</span><span>{stats.critical}</span>
                  </div>
                </div>
              </div>

              {/* >>> Operations Map (insérée ici) <<< */}
              <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
                <div className="text-slate-300 text-sm mb-2">Operations Map</div>
                <MapView
                  missions={missions}
                  onMarkerClick={handleMarkerClick}
                  className="mt-2"
                />
                {selected && (
                  <div className="mt-3 text-[12px] text-slate-400">
                    Selected: <span className="text-slate-200">{selected.title}</span> ({selected.status})
                  </div>
                )}
              </div>

              <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
                <div className="text-slate-300 text-sm mb-3">Quick Actions</div>
                <div className="grid grid-cols-2 gap-3">
                  <button className="rounded-xl border border-white/10 bg-slate-800/40 py-3">Resources</button>
                  <button className="rounded-xl border border-white/10 bg-slate-800/40 py-3">Personnel</button>
                  <button className="rounded-xl border border-white/10 bg-slate-800/40 py-3">Reports</button>
                  <button className="rounded-xl border border-white/10 bg-slate-800/40 py-3">Schedule</button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
