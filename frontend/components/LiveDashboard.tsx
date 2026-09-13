"use client";

import { AlertTriangle, Car, Search, Siren, TrafficCone } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { ApiError, getActiveIncidents, getLiveCongestion } from "@/lib/api";
import { RISK_STATUS, STATUS_COLOR } from "@/lib/status";
import type { Incident, LiveCorridorStatus, LocationSearchResult, RiskDay } from "@/lib/types";
import ApiErrorNotice from "./ApiErrorNotice";
import CorridorPanel from "./CorridorPanel";
import LocationSearch from "./LocationSearch";
import Reveal from "./Reveal";
import RiskBadge from "./RiskBadge";
import StatTile from "./StatTile";

const POLL_MS = 20_000;

async function safeLoad<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch (err) {
    if (err instanceof ApiError || err instanceof TypeError) return null;
    throw err;
  }
}

function secondsAgoLabel(seconds: number): string {
  if (seconds < 5) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  return `${Math.round(seconds / 60)}m ago`;
}

export default function LiveDashboard({
  initialCorridors,
  initialIncidents,
  today,
}: {
  initialCorridors: LiveCorridorStatus[] | null;
  initialIncidents: Incident[] | null;
  today: RiskDay | undefined;
}) {
  const [corridors, setCorridors] = useState(initialCorridors);
  const [incidents, setIncidents] = useState(initialIncidents);
  const [searchResult, setSearchResult] = useState<LocationSearchResult | null>(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [now, setNow] = useState(new Date());
  const [flash, setFlash] = useState(false);
  const [connected, setConnected] = useState(true);
  const pollingRef = useRef(false);

  useEffect(() => {
    const clock = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(clock);
  }, []);

  useEffect(() => {
    const poll = async () => {
      if (pollingRef.current) return;
      pollingRef.current = true;
      const [c, i] = await Promise.all([
        safeLoad<LiveCorridorStatus[]>(getLiveCongestion),
        safeLoad<Incident[]>(getActiveIncidents),
      ]);
      pollingRef.current = false;

      if (c === null && i === null) {
        setConnected(false);
        return;
      }
      setConnected(true);
      if (c !== null) setCorridors(c);
      if (i !== null) setIncidents(i);
      setLastUpdated(new Date());
      setFlash(true);
      setTimeout(() => setFlash(false), 900);
    };
    const id = setInterval(poll, POLL_MS);
    return () => clearInterval(id);
  }, []);

  const congestedCount =
    corridors?.filter((c) => c.latest_reading && c.latest_reading.severity !== "free_flow").length ?? null;
  const secondsAgo = Math.max(0, Math.round((now.getTime() - lastUpdated.getTime()) / 1000));

  return (
    <div className="flex flex-col gap-10">
      <Reveal>
        <section
          className="rounded-xl border border-[var(--border-hairline)] p-5"
          style={{
            background: `radial-gradient(circle at 15% 0%, ${STATUS_COLOR.good}14, transparent 55%), radial-gradient(circle at 100% 20%, var(--chart-line)14, transparent 45%)`,
          }}
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-semibold text-[var(--text-primary)]">At a glance</h1>
              <p className="mt-1 max-w-2xl text-sm text-[var(--text-secondary)]">
                Live status for the six exit corridors named in the{" "}
                <Link href="/case-study" className="underline underline-offset-2">
                  Sep 11 2026 exodus case study
                </Link>
                .
              </p>
            </div>
            <div
              className={`flex items-center gap-2 rounded-full border border-[var(--border-hairline)] bg-[var(--surface-1)] px-3 py-1.5 text-xs font-medium ${!connected ? "opacity-60" : ""}`}
            >
              <span
                className={`h-2 w-2 rounded-full ${connected ? "animate-live-pulse" : ""}`}
                style={{ backgroundColor: connected ? STATUS_COLOR.good : "var(--text-muted)" }}
                aria-hidden
              />
              <span className="text-[var(--text-primary)]">{connected ? "Live" : "Reconnecting…"}</span>
              <span className="text-[var(--text-muted)]">· updated {secondsAgoLabel(secondsAgo)}</span>
            </div>
          </div>

          <div
            className={`mt-4 grid grid-cols-2 gap-3 rounded-lg sm:grid-cols-4 ${flash ? "animate-fresh-flash" : ""}`}
          >
            <StatTile
              label="Today's risk"
              value={today ? <RiskBadge level={today.risk_level} /> : "—"}
              detail={today?.related_event ?? undefined}
              icon={<Siren size={16} />}
            />
            <StatTile
              label="Corridors monitored"
              value={corridors ? corridors.length : "—"}
              icon={<Car size={16} />}
            />
            <StatTile
              label="Corridors congested"
              value={congestedCount ?? "—"}
              detail={congestedCount ? "above free-flow" : undefined}
              accent={congestedCount ? STATUS_COLOR.warning : undefined}
              icon={<TrafficCone size={16} />}
            />
            <StatTile
              label="Active incidents"
              value={incidents ? incidents.length : "—"}
              accent={incidents && incidents.length > 0 ? STATUS_COLOR.serious : undefined}
              icon={<AlertTriangle size={16} />}
            />
          </div>
        </section>
      </Reveal>

      <Reveal delayMs={60}>
        <section>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-[var(--text-primary)]">
            <Search size={18} className="text-[var(--text-muted)]" aria-hidden />
            Check any location
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Not one of the six pinned corridors — search any city or address, in India or worldwide, for its
            real-time traffic speed. It drops a live pin on the satellite map below.
          </p>
          <div className="mt-4">
            <LocationSearch onResult={setSearchResult} />
          </div>
        </section>
      </Reveal>

      {today && today.risk_level !== "LOW" && (
        <Reveal delayMs={100}>
          <section
            className="rounded-lg border border-[var(--border-hairline)] p-4"
            style={{ backgroundColor: `${STATUS_COLOR[RISK_STATUS[today.risk_level]]}0d` }}
          >
            <div className="flex items-center gap-3">
              <RiskBadge level={today.risk_level} />
              {today.related_event && (
                <span className="text-sm font-medium text-[var(--text-primary)]">{today.related_event}</span>
              )}
            </div>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">{today.recommendation}</p>
            <Link
              href="/risk-calendar"
              className="mt-3 inline-block text-sm font-medium underline underline-offset-2"
            >
              View full risk calendar →
            </Link>
          </section>
        </Reveal>
      )}

      <Reveal delayMs={140}>
        <section>
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Corridors</h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            Live satellite view and ranked status in one place. The orange/red flow lines on the map are
            TomTom&apos;s live traffic overlay across every road in view, not just the six pins.
          </p>
          <div className="mt-4">
            <CorridorPanel corridors={corridors} searchMarker={searchResult} />
          </div>
        </section>
      </Reveal>

      <Reveal delayMs={220}>
        <section>
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Active incidents</h2>
          {incidents === null ? (
            <div className="mt-3">
              <ApiErrorNotice />
            </div>
          ) : incidents.length === 0 ? (
            <p className="mt-3 text-sm text-[var(--text-muted)]">No incidents reported in the last poll cycle.</p>
          ) : (
            <ul className="mt-3 flex flex-col gap-2">
              {incidents.slice(0, 8).map((incident) => (
                <li
                  key={incident.id}
                  className="flex items-start gap-3 rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)] p-3 text-sm"
                >
                  <AlertTriangle size={16} className="mt-0.5 shrink-0 text-[var(--text-muted)]" aria-hidden />
                  <div>
                    <p className="text-[var(--text-primary)]">{incident.description}</p>
                    <p className="mt-1 text-xs text-[var(--text-muted)]">
                      {incident.road_numbers || incident.icon_category} · delay magnitude{" "}
                      {incident.magnitude_of_delay}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </Reveal>
    </div>
  );
}
