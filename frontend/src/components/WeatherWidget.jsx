import { useEffect, useState } from "react";
import { fetchCurrentWeather } from "../api/weather";

export default function WeatherWidget({ lat, lon, title = "Weather Conditions" }) {
  const [w, setW] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const data = await fetchCurrentWeather({ lat, lon });
        if (alive) setW(data);
      } catch {
        if (alive) setErr("Météo indisponible");
      }
    })();
    return () => { alive = false; };
  }, [lat, lon]);

  const unit = (import.meta.env.VITE_OWM_UNITS || "metric") === "metric" ? "C" : "F";

  return (
    <div className="bg-slate-900/60 border border-white/10 rounded-xl p-4">
      <div className="text-slate-300 text-sm mb-2">{title}</div>

      {err && <div className="text-slate-500 text-sm">{err}</div>}
      {!err && !w && <div className="text-slate-500 text-sm">Chargement…</div>}

      {w && (
        <div className="flex items-center gap-4">
          <img
            src={`https://openweathermap.org/img/wn/${w.icon}@2x.png`}
            alt={w.desc}
            className="w-12 h-12" draggable="false"
          />
          <div>
            <div className="text-3xl font-semibold">{w.temp}°{unit}</div>
            <div className="text-slate-400 text-sm capitalize">
              {w.desc}{w.name ? ` • ${w.name}` : ""}
            </div>
            <div className="text-[12px] text-slate-500 mt-1">
              Vent {w.wind} • Humidité {w.humidity}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
