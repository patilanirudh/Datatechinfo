"use client";

import { useMemo, useState } from "react";
import { RISK_STATUS, STATUS_COLOR } from "@/lib/status";
import type { RiskDay, RiskLevel } from "@/lib/types";
import RiskBadge from "./RiskBadge";

const WEEKDAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const LEGEND_LEVELS: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

interface MonthBlock {
  label: string;
  weeks: (RiskDay | null)[][];
}

function buildMonths(days: RiskDay[]): MonthBlock[] {
  const byDate = new Map(days.map((d) => [d.date, d]));
  const start = new Date(`${days[0].date}T00:00:00`);
  const end = new Date(`${days[days.length - 1].date}T00:00:00`);

  const months: MonthBlock[] = [];
  const cursor = new Date(start.getFullYear(), start.getMonth(), 1);
  const lastMonth = new Date(end.getFullYear(), end.getMonth(), 1);

  while (cursor <= lastMonth) {
    const year = cursor.getFullYear();
    const month = cursor.getMonth();
    const firstOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const cells: (RiskDay | null)[] = [];
    for (let i = 0; i < firstOfMonth.getDay(); i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) {
      const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      cells.push(byDate.get(iso) ?? null);
    }
    while (cells.length % 7 !== 0) cells.push(null);

    const weeks: (RiskDay | null)[][] = [];
    for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));

    months.push({
      label: firstOfMonth.toLocaleDateString("en-IN", { month: "long", year: "numeric" }),
      weeks,
    });

    cursor.setMonth(cursor.getMonth() + 1);
  }

  return months;
}

export default function RiskCalendarGrid({ days }: { days: RiskDay[] }) {
  const months = useMemo(() => buildMonths(days), [days]);
  const [selected, setSelected] = useState<RiskDay>(days[0]);

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      <div className="flex-1">
        <div className="mb-4 flex flex-wrap items-center gap-4 text-xs text-[var(--text-secondary)]">
          {LEGEND_LEVELS.map((level) => (
            <span key={level} className="flex items-center gap-1.5">
              <span
                className="h-3 w-3 rounded-sm"
                style={{
                  backgroundColor: level === "LOW" ? "var(--gridline)" : `${STATUS_COLOR[RISK_STATUS[level]]}33`,
                  border: `1px solid ${level === "LOW" ? "var(--gridline)" : STATUS_COLOR[RISK_STATUS[level]]}`,
                }}
                aria-hidden
              />
              {level}
            </span>
          ))}
        </div>

        <div className="flex flex-col gap-8">
          {months.map((month) => (
            <div key={month.label}>
              <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">{month.label}</p>
              <div className="grid grid-cols-7 gap-1 text-center text-[10px] text-[var(--text-muted)]">
                {WEEKDAYS.map((w) => (
                  <div key={w} className="py-1">
                    {w}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {month.weeks.flat().map((day, i) => {
                  if (!day) return <div key={i} className="aspect-square" />;
                  const status = RISK_STATUS[day.risk_level];
                  const isLow = day.risk_level === "LOW";
                  const isSelected = selected.date === day.date;
                  const isToday = day.date === days[0].date;
                  return (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setSelected(day)}
                      aria-pressed={isSelected}
                      className="relative aspect-square rounded-sm text-xs font-medium transition-transform hover:scale-105 focus:outline focus:outline-2 focus:outline-offset-1"
                      style={{
                        backgroundColor: isLow ? "var(--gridline)" : `${STATUS_COLOR[status]}33`,
                        color: "var(--text-primary)",
                        outlineColor: isSelected ? "var(--chart-line)" : undefined,
                        boxShadow: isSelected ? "0 0 0 2px var(--chart-line) inset" : undefined,
                      }}
                    >
                      {day.date.slice(-2).replace(/^0/, "")}
                      {isToday && (
                        <span
                          className="absolute bottom-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full"
                          style={{ backgroundColor: "var(--chart-line)" }}
                          aria-hidden
                        />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:w-80 lg:shrink-0">
        <div className="sticky top-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)] p-4">
          <p className="text-xs text-[var(--text-muted)]">
            {new Date(`${selected.date}T00:00:00`).toLocaleDateString("en-IN", {
              weekday: "long",
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </p>
          <div className="mt-2">
            <RiskBadge level={selected.risk_level} />
          </div>
          {selected.related_event && (
            <p className="mt-2 text-sm font-medium text-[var(--text-primary)]">{selected.related_event}</p>
          )}
          <p className="mt-2 text-sm text-[var(--text-secondary)]">{selected.recommendation}</p>
          {selected.reasons.length > 0 && (
            <ul className="mt-3 list-inside list-disc text-xs text-[var(--text-muted)]">
              {selected.reasons.map((reason) => (
                <li key={reason} className="mt-1">
                  {reason}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
