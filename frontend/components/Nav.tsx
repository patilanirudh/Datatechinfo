import Link from "next/link";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/risk-calendar", label: "Risk Calendar" },
  { href: "/case-study", label: "Case Study" },
  { href: "/solutions", label: "Solutions" },
];

export default function Nav() {
  return (
    <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-black">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="flex flex-col leading-tight">
          <span className="text-lg font-semibold text-zinc-950 dark:text-zinc-50">
            Bengaluru Traffic Pulse
          </span>
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            Root-cause tracking for the recurring festival-weekend gridlock
          </span>
        </Link>
        <nav className="flex flex-wrap gap-1 text-sm font-medium">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-md px-3 py-1.5 text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-950 dark:text-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-zinc-50"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
