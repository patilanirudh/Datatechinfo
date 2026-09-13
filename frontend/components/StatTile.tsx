import type { ReactNode } from "react";

export default function StatTile({
  label,
  value,
  detail,
  accent,
  icon,
}: {
  label: string;
  value: ReactNode;
  detail?: string;
  accent?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="rounded-lg border border-[var(--border-hairline)] bg-[var(--surface-1)] p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-medium text-[var(--text-secondary)]">{label}</p>
        {icon && (
          <span className="text-[var(--text-muted)]" aria-hidden>
            {icon}
          </span>
        )}
      </div>
      <p
        className="mt-1.5 text-2xl font-semibold"
        style={{ color: accent ?? "var(--text-primary)" }}
      >
        {value}
      </p>
      {detail && <p className="mt-0.5 text-xs text-[var(--text-muted)]">{detail}</p>}
    </div>
  );
}
