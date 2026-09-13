import type { Severity } from "@/lib/types";

const STYLES: Record<Severity, string> = {
  free_flow: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  moderate: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300",
  severe: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
  closed: "bg-zinc-800 text-zinc-100 dark:bg-zinc-700 dark:text-zinc-100",
};

const LABELS: Record<Severity, string> = {
  free_flow: "Free flow",
  moderate: "Moderate",
  high: "High",
  severe: "Severe",
  closed: "Closed",
};

export default function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[severity]}`}
    >
      {LABELS[severity]}
    </span>
  );
}
