import { AlertOctagon, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { SEVERITY_LABEL, SEVERITY_STATUS, STATUS_BG_CLASS, STATUS_TEXT_CLASS } from "@/lib/status";
import type { Severity } from "@/lib/types";

const ICON: Record<Severity, typeof CheckCircle2> = {
  free_flow: CheckCircle2,
  moderate: AlertTriangle,
  high: AlertOctagon,
  severe: AlertOctagon,
  closed: XCircle,
};

export default function SeverityBadge({ severity }: { severity: Severity }) {
  const status = SEVERITY_STATUS[severity];
  const Icon = ICON[severity];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_BG_CLASS[status]} ${STATUS_TEXT_CLASS[status]}`}
    >
      <Icon size={12} strokeWidth={2.5} aria-hidden />
      {SEVERITY_LABEL[severity]}
    </span>
  );
}
