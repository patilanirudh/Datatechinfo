import type { ReactNode } from "react";

export default function Reveal({ children, delayMs = 0 }: { children: ReactNode; delayMs?: number }) {
  return (
    <div className="animate-reveal" style={{ animationDelay: `${delayMs}ms` }}>
      {children}
    </div>
  );
}
