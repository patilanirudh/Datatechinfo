"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { formatRatio } from "@/lib/format";
import { SEVERITY_STATUS, STATUS_COLOR } from "@/lib/status";
import type { LiveCorridorStatus, LocationSearchResult } from "@/lib/types";
import SeverityBadge from "./SeverityBadge";

const REFERENCE_CENTER: [number, number] = [12.9716, 77.5946]; // Bengaluru
const TOMTOM_KEY = process.env.NEXT_PUBLIC_TOMTOM_API_KEY;

function dotIcon(color: string, { pulse = false, size = 16 }: { pulse?: boolean; size?: number } = {}) {
  return L.divIcon({
    className: "",
    html: `<span style="display:block;width:${size}px;height:${size}px;border-radius:9999px;background:${color};border:2px solid var(--surface-1);box-shadow:0 0 0 1px ${color}66${pulse ? `,0 0 0 6px ${color}33` : ""}"${pulse ? ' class="animate-live-pulse"' : ""}></span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

function FlyToSearch({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lon], 13, { duration: 1.1 });
  }, [lat, lon, map]);
  return null;
}

export default function CorridorMap({
  corridors,
  searchMarker,
}: {
  corridors: LiveCorridorStatus[];
  searchMarker?: LocationSearchResult | null;
}) {
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
      {TOMTOM_KEY && (
        <TileLayer
          attribution="Traffic flow &copy; TomTom"
          url={`https://api.tomtom.com/traffic/map/4/tile/flow/relative0/{z}/{x}/{y}.png?key=${TOMTOM_KEY}`}
          opacity={0.75}
          maxZoom={18}
        />
      )}

      {corridors.map(({ corridor, latest_reading }) => {
        const color = latest_reading
          ? STATUS_COLOR[SEVERITY_STATUS[latest_reading.severity]]
          : "#898781";
        return (
          <Marker key={corridor.id} position={[corridor.lat, corridor.lon]} icon={dotIcon(color)}>
            <Popup>
              <div className="min-w-40">
                <p className="text-sm font-medium">{corridor.name}</p>
                <p className="text-xs text-zinc-500">{corridor.direction}</p>
                {latest_reading ? (
                  <div className="mt-2 flex items-center justify-between gap-2">
                    <span className="text-xs">{latest_reading.current_speed_kmh.toFixed(0)} km/h</span>
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

      {searchMarker && (
        <>
          <FlyToSearch lat={searchMarker.lat} lon={searchMarker.lon} />
          <Marker
            position={[searchMarker.lat, searchMarker.lon]}
            icon={dotIcon(STATUS_COLOR[SEVERITY_STATUS[searchMarker.severity]], { pulse: true, size: 20 })}
          >
            <Popup>
              <div className="min-w-40">
                <p className="text-sm font-medium">{searchMarker.freeform_address}</p>
                <div className="mt-2 flex items-center justify-between gap-2">
                  <span className="text-xs">
                    {searchMarker.current_speed_kmh.toFixed(0)} km/h ·{" "}
                    {formatRatio(searchMarker.congestion_ratio, searchMarker.severity)}
                  </span>
                  <SeverityBadge severity={searchMarker.severity} />
                </div>
              </div>
            </Popup>
          </Marker>
        </>
      )}
    </MapContainer>
  );
}
