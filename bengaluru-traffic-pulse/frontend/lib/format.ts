import type { Severity } from "./types";

/** road_closure readings report congestion_ratio as +Infinity server-side, which
 * serializes over JSON as null — never call .toFixed on it directly. */
export function formatRatio(ratio: number | null, severity: Severity): string {
  if (severity === "closed" || ratio === null) return "closed";
  return `${ratio.toFixed(2)}x`;
}

export function isFiniteRatio(ratio: number | null, severity: Severity): ratio is number {
  return severity !== "closed" && ratio !== null && Number.isFinite(ratio);
}
