import type {
  CaseStudy,
  Corridor,
  CongestionReading,
  Incident,
  LiveCorridorStatus,
  LocationSearchResult,
  RiskDay,
  Solutions,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public readonly path: string,
    public readonly status: number,
    public readonly detail?: string,
  ) {
    super(detail ?? `Request to ${path} failed with status ${status}`);
  }
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined);
    throw new ApiError(path, res.status, detail);
  }
  return res.json() as Promise<T>;
}

export function getCorridors(): Promise<Corridor[]> {
  return apiFetch<Corridor[]>("/api/corridors");
}

export function getLiveCongestion(): Promise<LiveCorridorStatus[]> {
  return apiFetch<LiveCorridorStatus[]>("/api/congestion/live");
}

export function getCongestionHistory(corridorId: string, hours = 24): Promise<CongestionReading[]> {
  return apiFetch<CongestionReading[]>(
    `/api/congestion/history?corridor_id=${encodeURIComponent(corridorId)}&hours=${hours}`,
  );
}

export function getActiveIncidents(): Promise<Incident[]> {
  return apiFetch<Incident[]>("/api/incidents/active");
}

export function getRiskCalendar(days = 60): Promise<RiskDay[]> {
  return apiFetch<RiskDay[]>(`/api/risk-calendar?days=${days}`);
}

export function getCaseStudy(): Promise<CaseStudy> {
  return apiFetch<CaseStudy>("/api/case-study");
}

export function getSolutions(): Promise<Solutions> {
  return apiFetch<Solutions>("/api/solutions");
}

export function searchLocation(query: string): Promise<LocationSearchResult> {
  return apiFetch<LocationSearchResult>(`/api/congestion/search?q=${encodeURIComponent(query)}`);
}

export { ApiError, API_BASE_URL };
