import ApiErrorNotice from "@/components/ApiErrorNotice";
import RiskCalendarGrid from "@/components/RiskCalendarGrid";
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

export default async function RiskCalendarPage() {
  const days = await safeLoad<RiskDay[]>(() => getRiskCalendar(60));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Risk calendar</h1>
        <p className="mt-1 max-w-2xl text-sm text-[var(--text-secondary)]">
          A transparent, rule-based forecast — not a machine-learned model — built from Karnataka&apos;s
          published holiday calendar and the exodus pattern documented in the Sep 11 2026 case study.
          Click any date for its full reasoning and recommendation.
        </p>
      </div>

      {days === null ? <ApiErrorNotice /> : <RiskCalendarGrid days={days} />}
    </div>
  );
}
