import LiveDashboard from "@/components/LiveDashboard";
import { ApiError, getActiveIncidents, getLiveCongestion, getRiskCalendar } from "@/lib/api";
import type { Incident, LiveCorridorStatus, RiskDay } from "@/lib/types";

export const dynamic = "force-dynamic";

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

  return (
    <LiveDashboard initialCorridors={corridors} initialIncidents={incidents} today={riskDays?.[0]} />
  );
}
