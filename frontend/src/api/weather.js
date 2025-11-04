import axios from "axios";

const BASE = "https://api.openweathermap.org/data/2.5";
const KEY  = import.meta.env.VITE_OWM_KEY;
const UNITS = import.meta.env.VITE_OWM_UNITS || "metric"; // C/F/K

export async function fetchCurrentWeather({ lat, lon }) {
  if (lat == null || lon == null) throw new Error("lat/lon required");
  const { data } = await axios.get(`${BASE}/weather`, {
    params: { lat, lon, appid: KEY, units: UNITS, lang: "fr" },
  });
  return {
    temp: Math.round(data.main.temp),
    desc: data.weather?.[0]?.description || "",
    icon: data.weather?.[0]?.icon || "01d",
    wind: Math.round(data.wind?.speed ?? 0),
    humidity: data.main?.humidity ?? 0,
    name: data.name || "",
  };
}