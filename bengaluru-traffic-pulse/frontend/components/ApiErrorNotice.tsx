import { WifiOff } from "lucide-react";

export default function ApiErrorNotice({ message }: { message?: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-dashed border-[var(--border-hairline)] bg-[var(--gridline)]/30 p-6 text-sm text-[var(--text-secondary)]">
      <WifiOff size={18} className="mt-0.5 shrink-0 text-[var(--text-muted)]" aria-hidden />
      <div>
        <p className="font-medium text-[var(--text-primary)]">Couldn&apos;t reach the API</p>
        <p className="mt-1">
          {message ??
            "The backend isn't responding. Make sure it's running and NEXT_PUBLIC_API_BASE_URL points at it."}
        </p>
      </div>
    </div>
  );
}
