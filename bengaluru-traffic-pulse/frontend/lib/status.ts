import type { RiskLevel, Severity } from "./types";

export type StatusRole = "good" | "warning" | "serious" | "critical";

export const SEVERITY_STATUS: Record<Severity, StatusRole> = {
  free_flow: "good",
  moderate: "warning",
  high: "serious",
  severe: "critical",
  closed: "critical",
};

export const RISK_STATUS: Record<RiskLevel, StatusRole> = {
  LOW: "good",
  MEDIUM: "warning",
  HIGH: "serious",
  CRITICAL: "critical",
};

export const SEVERITY_LABEL: Record<Severity, string> = {
  free_flow: "Free flow",
  moderate: "Moderate",
  high: "High",
  severe: "Severe",
  closed: "Closed",
};

// Status palette (fixed — never themed; see dataviz skill references/palette.md).
// Same four hex values in light and dark: all four clear 3:1 against the dark
// chart surface, and the light-mode sub-3:1 pairs (warning/serious) are always
// shipped with an icon + label, never color alone.
export const STATUS_COLOR: Record<StatusRole, string> = {
  good: "#0ca30c",
  warning: "#fab219",
  serious: "#ec835a",
  critical: "#d03b3b",
};

export const STATUS_TEXT_CLASS: Record<StatusRole, string> = {
  good: "text-[#0ca30c] dark:text-[#0ca30c]",
  warning: "text-[#a66c00] dark:text-[#fab219]",
  serious: "text-[#b34e2c] dark:text-[#ec835a]",
  critical: "text-[#d03b3b] dark:text-[#e66767]",
};

export const STATUS_BG_CLASS: Record<StatusRole, string> = {
  good: "bg-[#0ca30c]/10",
  warning: "bg-[#fab219]/15",
  serious: "bg-[#ec835a]/15",
  critical: "bg-[#d03b3b]/10",
};
