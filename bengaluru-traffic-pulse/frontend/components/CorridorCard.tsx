"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { ApiError, getCongestionHistory } from "@/lib/api";
import { formatRatio, isFiniteRatio } from "@/lib/format";
import type { LiveCorridorStatus } from "@/lib/types";
import MiniLineChart from "./MiniLineChart";
import SeverityBadge from "./SeverityBadge";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  return `${hours} hr ago`;
}

type HistoryState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error" }
  | { status: "ready"; points: { t: number; y: number }[] };

export default function CorridorCard({ corridor, latest_reading, stale }: LiveCorridorStatus) {
  const [open, setOpen] = useState(false);
  const [history, setHistory] = useState<HistoryState>({ status: "idle" });

  async function handleToggle() {
    const next = !open;
    setOpen(next);
    if (next && history.status === "idle") {
      setHistory({ status: "loading" });
      try {
        const readings = await getCongestionHistory(corridor.id, 24);
        setHistory({
          status: "ready",
          points: readings
            .filter((r) => isFiniteRatio(r.congestion_ratio, r.severity))
            .map((r) => ({ t: new Date(r.recorded_at).getTime(), y: r.congestion_ratio as number })),
        });
      } catch (err) {
        if (err instanceof ApiError || err instanceof TypeError) {
          setHistory({ status: "error" });
        } else {
          throw err;
        }
      }
    }
  }

  return (
    <div className="rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)] transition-shadow hover:shadow-md">
      <button
        type="button"
        onClick={handleToggle}
        aria-expanded={open}
        className="flex w-full flex-col gap-3 p-4 text-left"
      >
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="font-medium text-[var(--text-primary)]">{corridor.name}</p>
            <p className="text-xs text-[var(--text-muted)]">{corridor.direction}</p>
          </div>
          {latest_reading && <SeverityBadge severity={latest_reading.severity} />}
        </div>

        {latest_reading ? (
          <div className="flex items-end justify-between text-sm">
            <div>
              <p className="text-[var(--text-secondary)]">
                {latest_reading.current_speed_kmh.toFixed(0)} km/h
                <span className="text-[var(--text-muted)]">
                  {" "}
                  / {latest_reading.free_flow_speed_kmh.toFixed(0)} free-flow
                </span>
              </p>
              <p className="text-xs text-[var(--text-muted)]">
                {formatRatio(latest_reading.congestion_ratio, latest_reading.severity)} travel time
                {stale && " · stale"}
              </p>
            </div>
            <div className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
              {timeAgo(latest_reading.recorded_at)}
              <ChevronDown
                size={14}
                className={`transition-transform ${open ? "rotate-180" : ""}`}
                aria-hidden
              />
            </div>
          </div>
        ) : (
          <p className="text-sm text-[var(--text-muted)]">
            No readings yet — ingestion runs every ~15 min.
          </p>
        )}
      </button>

      {open && (
        <div className="border-t border-[var(--border-hairline)] px-4 pb-4 pt-3">
          <p className="mb-1 text-xs font-medium text-[var(--text-secondary)]">Last 24 hours</p>
          {history.status === "loading" && (
            <p className="py-6 text-center text-sm text-[var(--text-muted)]">Loading…</p>
          )}
          {history.status === "error" && (
            <p className="py-6 text-center text-sm text-[var(--text-muted)]">
              Couldn&apos;t load history for this corridor.
            </p>
          )}
          {history.status === "ready" && <MiniLineChart points={history.points} />}
        </div>
      )}
    </div>
  );
}
