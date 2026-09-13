import { Bike, Bus, Car, Satellite } from "lucide-react";
import ApiErrorNotice from "./ApiErrorNotice";
import CorridorMapClient from "./CorridorMapClient";
import CorridorRow from "./CorridorRow";
import type { LiveCorridorStatus, LocationSearchResult } from "@/lib/types";

export default function CorridorPanel({
  corridors,
  searchMarker,
}: {
  corridors: LiveCorridorStatus[] | null;
  searchMarker?: LocationSearchResult | null;
}) {
  if (corridors === null) {
    return <ApiErrorNotice />;
  }

  const finiteRatios = corridors
    .map((c) => c.latest_reading?.congestion_ratio)
    .filter((r): r is number => r !== null && r !== undefined && Number.isFinite(r));
  const domainMax = Math.max(2, Math.ceil(Math.max(1, ...finiteRatios) * 2) / 2);

  const sorted = [...corridors].sort((a, b) => {
    const aClosed = a.latest_reading?.severity === "closed";
    const bClosed = b.latest_reading?.severity === "closed";
    if (aClosed !== bClosed) return aClosed ? -1 : 1;
    if (!a.latest_reading) return 1;
    if (!b.latest_reading) return -1;
    return (b.latest_reading.congestion_ratio ?? 0) - (a.latest_reading.congestion_ratio ?? 0);
  });

  return (
    <div className="overflow-hidden rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)]">
      <div className="p-4">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-[var(--text-primary)]">
          <Satellite size={16} className="text-[var(--text-muted)]" aria-hidden />
          Satellite view
        </h3>
        <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-muted)]">
          <span>Pinned and color-coded by current severity — search above to drop a live pin anywhere.</span>
          <span className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Car size={13} aria-hidden /> private vehicles
            </span>
            <span className="flex items-center gap-1">
              <Bus size={13} aria-hidden /> KSRTC buses
            </span>
            <span className="flex items-center gap-1">
              <Bike size={13} aria-hidden /> two-wheelers
            </span>
          </span>
        </p>
      </div>
      <div className="px-4">
        <CorridorMapClient corridors={corridors} searchMarker={searchMarker} />
      </div>

      <div className="mt-4 border-t border-[var(--border-hairline)]">
        <div className="flex items-center justify-between px-4 py-2">
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">
            Ranked by congestion — click a corridor for its 24h trend
          </h3>
        </div>
        {sorted.map((c) => (
          <CorridorRow key={c.corridor.id} {...c} domainMax={domainMax} />
        ))}
      </div>
    </div>
  );
}
