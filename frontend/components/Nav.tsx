import { BookOpen, CalendarDays, LayoutDashboard, Lightbulb } from "lucide-react";
import Link from "next/link";

const LINKS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/risk-calendar", label: "Risk Calendar", icon: CalendarDays },
  { href: "/case-study", label: "Case Study", icon: BookOpen },
  { href: "/solutions", label: "Solutions", icon: Lightbulb },
];

export default function Nav() {
  return (
    <header className="border-b border-[var(--border-hairline)] bg-[var(--surface-1)]">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="flex flex-col leading-tight">
          <span className="text-lg font-semibold text-[var(--text-primary)]">
            Bengaluru Traffic Pulse
          </span>
          <span className="text-xs text-[var(--text-muted)]">
            Root-cause tracking for the recurring festival-weekend gridlock
          </span>
        </Link>
        <nav className="flex flex-wrap gap-1 text-sm font-medium">
          {LINKS.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-[var(--text-secondary)] transition-colors hover:bg-[var(--gridline)]/60 hover:text-[var(--text-primary)]"
              >
                <Icon size={15} aria-hidden />
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
