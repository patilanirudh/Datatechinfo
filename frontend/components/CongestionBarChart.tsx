import { formatRatio } from "@/lib/format";
import { SEVERITY_STATUS, STATUS_COLOR } from "@/lib/status";
import type { LiveCorridorStatus } from "@/lib/types";

export default function CongestionBarChart({ corridors }: { corridors: LiveCorridorStatus[] }) {
  const withReadings = corridors
    .filter((c) => c.latest_reading !== null)
    .map((c) => ({ ...c, latest_reading: c.latest_reading! }))
    .sort((a, b) => {
      const aClosed = a.latest_reading.severity === "closed";
      const bClosed = b.latest_reading.severity === "closed";
      if (aClosed !== bClosed) return aClosed ? -1 : 1; // closed roads sort first, as the worst case
      return (b.latest_reading.congestion_ratio ?? 0) - (a.latest_reading.congestion_ratio ?? 0);
    });

  const missing = corridors.filter((c) => c.latest_reading === null);

  if (withReadings.length === 0) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        No live readings yet to compare — check back once ingestion has run.
      </p>
    );
  }

  const finiteRatios = withReadings
    .map((c) => c.latest_reading.congestion_ratio)
    .filter((r): r is number => r !== null && Number.isFinite(r));
  const domainMax = Math.max(2, Math.ceil(Math.max(1, ...finiteRatios) * 2) / 2);

  return (
    <div>
      <div className="flex flex-col gap-3">
        {withReadings.map(({ corridor, latest_reading }) => {
          const status = SEVERITY_STATUS[latest_reading.severity];
          const color = STATUS_COLOR[status];
          const closed = latest_reading.severity === "closed";
          const widthPct = closed
            ? 100
            : Math.max(3, (((latest_reading.congestion_ratio ?? 1) - 1) / (domainMax - 1)) * 100);
          return (
            <div key={corridor.id} className="group relative">
              <div className="mb-1 flex items-baseline justify-between gap-2 text-xs">
                <span className="truncate text-[var(--text-secondary)]">{corridor.name}</span>
              </div>
              <div
                tabIndex={0}
                className="relative h-6 rounded-sm bg-[var(--gridline)] outline-none"
              >
                <div
                  className="flex h-6 items-center justify-end rounded-r-sm pr-2 transition-[width] duration-300"
                  style={{ width: `${widthPct}%`, backgroundColor: color, minWidth: "2.75rem" }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatRatio(latest_reading.congestion_ratio, latest_reading.severity)}
                  </span>
                </div>
                <div
                  role="tooltip"
                  className="pointer-events-none absolute -top-9 left-0 z-10 whitespace-nowrap rounded-md border border-[var(--border-hairline)] bg-[var(--surface-1)] px-2 py-1 text-xs text-[var(--text-primary)] opacity-0 shadow-sm transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
                >
                  {closed
                    ? "Road closed"
                    : `${latest_reading.current_speed_kmh.toFixed(0)} km/h of ${latest_reading.free_flow_speed_kmh.toFixed(0)} km/h free-flow`}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {missing.length > 0 && (
        <p className="mt-3 text-xs text-[var(--text-muted)]">
          No reading yet: {missing.map((c) => c.corridor.name).join(", ")}
        </p>
      )}
    </div>
  );
}
