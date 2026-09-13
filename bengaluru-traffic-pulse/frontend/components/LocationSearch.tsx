"use client";

import { Navigation, Search } from "lucide-react";
import { useState } from "react";
import { ApiError, searchLocation } from "@/lib/api";
import { formatRatio } from "@/lib/format";
import type { LocationSearchResult } from "@/lib/types";
import SeverityBadge from "./SeverityBadge";

type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; result: LocationSearchResult };

export default function LocationSearch({
  onResult,
}: {
  onResult?: (result: LocationSearchResult | null) => void;
}) {
  const [query, setQuery] = useState("");
  const [state, setState] = useState<State>({ status: "idle" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setState({ status: "loading" });
    onResult?.(null);
    try {
      const result = await searchLocation(q);
      setState({ status: "ready", result });
      onResult?.(result);
    } catch (err) {
      if (err instanceof ApiError) {
        setState({ status: "error", message: err.detail ?? "Search failed." });
      } else if (err instanceof TypeError) {
        setState({ status: "error", message: "Couldn't reach the API." });
      } else {
        throw err;
      }
    }
  }

  return (
    <div className="rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)] p-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={16}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
            aria-hidden
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search any city or address, in India or worldwide…"
            className="w-full rounded-md border border-[var(--border-hairline)] bg-[var(--background)] py-2 pl-9 pr-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--chart-line)]"
          />
        </div>
        <button
          type="submit"
          disabled={state.status === "loading"}
          className="rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          style={{ backgroundColor: "var(--chart-line)" }}
        >
          {state.status === "loading" ? "Searching…" : "Search"}
        </button>
      </form>

      {state.status === "error" && (
        <p className="mt-3 text-sm text-[var(--text-muted)]">{state.message}</p>
      )}

      {state.status === "ready" && (
        <div className="mt-4 flex items-start justify-between gap-3 rounded-md border border-[var(--border-hairline)] p-3">
          <div className="flex items-start gap-2">
            <Navigation size={16} className="mt-0.5 shrink-0 text-[var(--text-muted)]" aria-hidden />
            <div>
              <p className="text-sm font-medium text-[var(--text-primary)]">
                {state.result.freeform_address}
              </p>
              <p className="mt-0.5 text-xs text-[var(--text-muted)]">
                {state.result.current_speed_kmh.toFixed(0)} km/h of{" "}
                {state.result.free_flow_speed_kmh.toFixed(0)} km/h free-flow ·{" "}
                {formatRatio(state.result.congestion_ratio, state.result.severity)} travel time
              </p>
            </div>
          </div>
          <SeverityBadge severity={state.result.severity} />
        </div>
      )}
    </div>
  );
}
