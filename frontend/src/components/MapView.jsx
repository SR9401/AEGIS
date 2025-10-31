import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

const DefaultIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function MapView({ missions = [], center=[48.8566, 2.3522], zoom=5, className="" }) {
  return (
    <div className={className}>
      <MapContainer center={center} zoom={zoom} className="h-80 w-full rounded-2xl overflow-hidden border border-white/10">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
        />
        {missions
          .filter(m => m.lat != null && m.lon != null)
          .map(m => (
            <Marker key={m.id} position={[m.lat, m.lon]}>
              <Popup>
                <div className="text-sm">
                  <div className="font-semibold">{m.title}</div>
                  <div className="text-slate-600">{m.status}</div>
                  {m.date && <div className="text-slate-500">{m.date.slice(0,16)}</div>}
                </div>
              </Popup>
            </Marker>
          ))}
      </MapContainer>
    </div>
  );
}
