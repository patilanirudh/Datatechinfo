import { AlertOctagon, AlertTriangle, CheckCircle2, Siren } from "lucide-react";
import { RISK_STATUS, STATUS_BG_CLASS, STATUS_TEXT_CLASS } from "@/lib/status";
import type { RiskLevel } from "@/lib/types";

const ICON: Record<RiskLevel, typeof CheckCircle2> = {
  LOW: CheckCircle2,
  MEDIUM: AlertTriangle,
  HIGH: AlertOctagon,
  CRITICAL: Siren,
};

export default function RiskBadge({ level }: { level: RiskLevel }) {
  const status = RISK_STATUS[level];
  const Icon = ICON[level];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_BG_CLASS[status]} ${STATUS_TEXT_CLASS[status]}`}
    >
      <Icon size={12} strokeWidth={2.5} aria-hidden />
      {level}
    </span>
  );
}
