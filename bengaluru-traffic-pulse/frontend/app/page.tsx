import Link from "next/link";
import ApiErrorNotice from "@/components/ApiErrorNotice";
import RiskBadge from "@/components/RiskBadge";
import SeverityBadge from "@/components/SeverityBadge";
import { ApiError, getActiveIncidents, getLiveCongestion, getRiskCalendar } from "@/lib/api";
import type { Incident, LiveCorridorStatus, RiskDay } from "@/lib/types";

export const dynamic = "force-dynamic";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  return `${hours} hr ago`;
}

async function safeLoad<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch (err) {
    if (err instanceof ApiError || err instanceof TypeError) return null;
    throw err;
  }
}

export default async function DashboardPage() {
  const [corridors, incidents, riskDays] = await Promise.all([
    safeLoad<LiveCorridorStatus[]>(getLiveCongestion),
    safeLoad<Incident[]>(getActiveIncidents),
    safeLoad<RiskDay[]>(() => getRiskCalendar(1)),
  ]);

  const today = riskDays?.[0];

  return (
    <div className="flex flex-col gap-10">
      <section>
        <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">
          Live corridor status
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
          Six exit corridors named in the{" "}
          <Link href="/case-study" className="underline underline-offset-2">
            Sep 11 2026 exodus case study
          </Link>
          , polled from TomTom every ~15 minutes.
        </p>

        {corridors === null ? (
          <div className="mt-4">
            <ApiErrorNotice />
          </div>
        ) : corridors.length === 0 ? (
          <p className="mt-4 text-sm text-zinc-500">No corridors configured.</p>
        ) : (
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {corridors.map(({ corridor, latest_reading, stale }) => (
              <div
                key={corridor.id}
                className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-medium text-zinc-950 dark:text-zinc-50">{corridor.name}</p>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">{corridor.direction}</p>
                  </div>
                  {latest_reading && <SeverityBadge severity={latest_reading.severity} />}
                </div>

                {latest_reading ? (
                  <div className="mt-3 flex items-end justify-between text-sm">
                    <div>
                      <p className="text-zinc-600 dark:text-zinc-400">
                        {latest_reading.current_speed_kmh.toFixed(0)} km/h
                        <span className="text-zinc-400 dark:text-zinc-600">
                          {" "}
                          / {latest_reading.free_flow_speed_kmh.toFixed(0)} free-flow
                        </span>
                      </p>
                      <p className="text-xs text-zinc-500 dark:text-zinc-500">
                        {latest_reading.congestion_ratio.toFixed(2)}x travel time
                        {stale && " · stale"}
                      </p>
                    </div>
                    <p className="text-xs text-zinc-400 dark:text-zinc-600">
                      {timeAgo(latest_reading.recorded_at)}
                    </p>
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-zinc-400 dark:text-zinc-600">
                    No readings yet — ingestion runs every ~15 min.
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-950 dark:text-zinc-50">Today&apos;s risk</h2>
        {today === undefined ? (
          <div className="mt-3">
            <ApiErrorNotice />
          </div>
        ) : (
          <div className="mt-3 rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="flex items-center gap-3">
              <RiskBadge level={today.risk_level} />
              {today.related_event && (
                <span className="text-sm text-zinc-600 dark:text-zinc-400">{today.related_event}</span>
              )}
            </div>
            <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">{today.recommendation}</p>
            <Link
              href="/risk-calendar"
              className="mt-3 inline-block text-sm font-medium underline underline-offset-2"
            >
              View full risk calendar →
            </Link>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-950 dark:text-zinc-50">Active incidents</h2>
        {incidents === null ? (
          <div className="mt-3">
            <ApiErrorNotice />
          </div>
        ) : incidents.length === 0 ? (
          <p className="mt-3 text-sm text-zinc-500">No incidents reported in the last hour.</p>
        ) : (
          <ul className="mt-3 flex flex-col gap-2">
            {incidents.slice(0, 8).map((incident) => (
              <li
                key={incident.id}
                className="rounded-lg border border-zinc-200 bg-white p-3 text-sm dark:border-zinc-800 dark:bg-zinc-950"
              >
                <p className="text-zinc-800 dark:text-zinc-200">{incident.description}</p>
                <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-500">
                  {incident.road_numbers || incident.icon_category} · delay magnitude{" "}
                  {incident.magnitude_of_delay}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
