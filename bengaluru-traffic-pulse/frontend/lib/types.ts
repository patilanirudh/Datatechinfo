export interface Corridor {
  id: string;
  name: string;
  lat: number;
  lon: number;
  direction: string;
}

export type Severity = "free_flow" | "moderate" | "high" | "severe" | "closed";

export interface CongestionReading {
  corridor_id: string;
  recorded_at: string;
  current_speed_kmh: number;
  free_flow_speed_kmh: number;
  current_travel_time_s: number;
  free_flow_travel_time_s: number;
  confidence: number;
  road_closure: boolean;
  /** +Infinity server-side for a closed road, which serializes over JSON as null. */
  congestion_ratio: number | null;
  severity: Severity;
}

export interface LiveCorridorStatus {
  corridor: Corridor;
  latest_reading: CongestionReading | null;
  stale: boolean;
}

export interface Incident {
  id: string;
  description: string;
  icon_category: string;
  magnitude_of_delay: number;
  road_numbers: string;
  start_time: string | null;
  end_time: string | null;
  lat: number;
  lon: number;
}

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface RiskDay {
  date: string;
  risk_level: RiskLevel;
  score: number;
  reasons: string[];
  recommendation: string;
  related_event: string | null;
}

export interface SolutionItem {
  title: string;
  description: string;
}

export interface SolutionGroup {
  label: string;
  items: SolutionItem[];
}

export interface Solutions {
  personal: SolutionGroup;
  systemic: SolutionGroup;
}

export interface CaseStudy {
  markdown: string;
}

export interface LocationSearchResult {
  query: string;
  freeform_address: string;
  lat: number;
  lon: number;
  current_speed_kmh: number;
  free_flow_speed_kmh: number;
  congestion_ratio: number | null;
  severity: Severity;
}
