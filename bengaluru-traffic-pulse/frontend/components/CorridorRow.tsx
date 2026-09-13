"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { ApiError, getCongestionHistory } from "@/lib/api";
import { formatRatio, isFiniteRatio } from "@/lib/format";
import { SEVERITY_STATUS, STATUS_COLOR } from "@/lib/status";
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

export default function CorridorRow({
  corridor,
  latest_reading,
  stale,
  domainMax,
}: LiveCorridorStatus & { domainMax: number }) {
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

  const closed = latest_reading?.severity === "closed";
  const barColor = latest_reading ? STATUS_COLOR[SEVERITY_STATUS[latest_reading.severity]] : "var(--gridline)";
  const widthPct = !latest_reading
    ? 0
    : closed
      ? 100
      : Math.max(4, (((latest_reading.congestion_ratio ?? 1) - 1) / (domainMax - 1)) * 100);

  return (
    <div className="border-b border-[var(--border-hairline)] last:border-b-0">
      <button
        type="button"
        onClick={handleToggle}
        aria-expanded={open}
        className="flex w-full flex-wrap items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-[var(--gridline)]/25"
      >
        <div className="w-full min-w-0 sm:w-44 sm:shrink-0">
          <p className="truncate text-sm font-medium text-[var(--text-primary)]">{corridor.name}</p>
          <p className="truncate text-xs text-[var(--text-muted)]">{corridor.direction}</p>
        </div>

        {latest_reading ? (
          <>
            <div className="min-w-[7rem] flex-1">
              <div className="h-4 overflow-hidden rounded-sm bg-[var(--gridline)]">
                <div
                  className="h-4 rounded-r-sm transition-[width] duration-500"
                  style={{ width: `${widthPct}%`, backgroundColor: barColor }}
                />
              </div>
            </div>
            <div className="w-24 shrink-0 text-right text-xs text-[var(--text-secondary)]">
              {formatRatio(latest_reading.congestion_ratio, latest_reading.severity)}
              {stale && " · stale"}
            </div>
            <SeverityBadge severity={latest_reading.severity} />
            <div className="flex w-24 shrink-0 items-center justify-end gap-1 text-xs text-[var(--text-muted)]">
              {timeAgo(latest_reading.recorded_at)}
              <ChevronDown size={14} className={`transition-transform ${open ? "rotate-180" : ""}`} aria-hidden />
            </div>
          </>
        ) : (
          <p className="flex-1 text-sm text-[var(--text-muted)]">No reading yet</p>
        )}
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1">
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
