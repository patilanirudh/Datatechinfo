import ApiErrorNotice from "@/components/ApiErrorNotice";
import RiskBadge from "@/components/RiskBadge";
import { ApiError, getRiskCalendar } from "@/lib/api";
import type { RiskDay } from "@/lib/types";

export const dynamic = "force-dynamic";

async function safeLoad<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch (err) {
    if (err instanceof ApiError || err instanceof TypeError) return null;
    throw err;
  }
}

function formatDate(iso: string): { weekday: string; label: string } {
  const d = new Date(`${iso}T00:00:00`);
  return {
    weekday: d.toLocaleDateString("en-IN", { weekday: "short" }),
    label: d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }),
  };
}

const ROW_STYLES: Record<RiskDay["risk_level"], string> = {
  LOW: "",
  MEDIUM: "bg-amber-50 dark:bg-amber-950/20",
  HIGH: "bg-orange-50 dark:bg-orange-950/20",
  CRITICAL: "bg-red-50 dark:bg-red-950/20",
};

export default async function RiskCalendarPage() {
  const days = await safeLoad<RiskDay[]>(() => getRiskCalendar(60));

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Risk calendar</h1>
        <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">
          A transparent, rule-based forecast — not a machine-learned model — built from Karnataka&apos;s
          published holiday calendar and the exodus pattern documented in the Sep 11 2026 case study.
          HIGH and CRITICAL days come with a concrete departure-window recommendation.
        </p>
      </div>

      {days === null ? (
        <ApiErrorNotice />
      ) : (
        <div className="flex flex-col divide-y divide-zinc-200 overflow-hidden rounded-lg border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
          {days
            .filter((d) => d.risk_level !== "LOW")
            .map((day) => {
              const { weekday, label } = formatDate(day.date);
              return (
                <details key={day.date} className={`group px-4 py-3 ${ROW_STYLES[day.risk_level]}`}>
                  <summary className="flex cursor-pointer list-none flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <span className="w-24 shrink-0 text-sm text-zinc-600 dark:text-zinc-400">
                        {weekday} {label}
                      </span>
                      <RiskBadge level={day.risk_level} />
                      {day.related_event && (
                        <span className="text-sm text-zinc-800 dark:text-zinc-200">
                          {day.related_event}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-zinc-400 dark:text-zinc-600">
                      score {day.score} · details ▾
                    </span>
                  </summary>
                  <div className="mt-2 pl-[7.5rem] text-sm">
                    <p className="text-zinc-700 dark:text-zinc-300">{day.recommendation}</p>
                    <ul className="mt-2 list-inside list-disc text-xs text-zinc-500 dark:text-zinc-500">
                      {day.reasons.map((reason) => (
                        <li key={reason}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                </details>
              );
            })}
          {days.every((d) => d.risk_level === "LOW") && (
            <p className="px-4 py-6 text-sm text-zinc-500">
              No elevated-risk days in the next {days.length} days.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
