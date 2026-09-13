"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { SEVERITY_STATUS, STATUS_COLOR } from "@/lib/status";
import type { LiveCorridorStatus } from "@/lib/types";
import SeverityBadge from "./SeverityBadge";

const REFERENCE_CENTER: [number, number] = [12.9716, 77.5946]; // Bengaluru

function dotIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<span style="display:block;width:16px;height:16px;border-radius:9999px;background:${color};border:2px solid var(--surface-1);box-shadow:0 0 0 1px ${color}66"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
    popupAnchor: [0, -8],
  });
}

export default function CorridorMap({ corridors }: { corridors: LiveCorridorStatus[] }) {
  return (
    <MapContainer
      center={REFERENCE_CENTER}
      zoom={11}
      scrollWheelZoom={false}
      className="h-[420px] w-full rounded-lg"
      style={{ background: "var(--gridline)" }}
    >
      <TileLayer
        attribution="Tiles &copy; Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        maxZoom={18}
      />
      {corridors.map(({ corridor, latest_reading }) => {
        const color = latest_reading
          ? STATUS_COLOR[SEVERITY_STATUS[latest_reading.severity]]
          : "#898781";
        return (
          <Marker
            key={corridor.id}
            position={[corridor.lat, corridor.lon]}
            icon={dotIcon(color)}
          >
            <Popup>
              <div className="min-w-40">
                <p className="text-sm font-medium">{corridor.name}</p>
                <p className="text-xs text-zinc-500">{corridor.direction}</p>
                {latest_reading ? (
                  <div className="mt-2 flex items-center justify-between gap-2">
                    <span className="text-xs">
                      {latest_reading.current_speed_kmh.toFixed(0)} km/h
                    </span>
                    <SeverityBadge severity={latest_reading.severity} />
                  </div>
                ) : (
                  <p className="mt-2 text-xs text-zinc-500">No reading yet</p>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}
