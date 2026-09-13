"use client";

import { useMemo, useState } from "react";

interface Point {
  t: number; // epoch ms
  y: number;
}

const WIDTH = 600;
const HEIGHT = 160;
const PAD_LEFT = 8;
const PAD_RIGHT = 8;
const PAD_TOP = 16;
const PAD_BOTTOM = 24;

export default function MiniLineChart({ points }: { points: Point[] }) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);

  const sorted = useMemo(() => [...points].sort((a, b) => a.t - b.t), [points]);

  if (sorted.length < 2) {
    return (
      <p className="py-6 text-center text-sm text-[var(--text-muted)]">
        Not enough history yet — check back after a few more ingestion polls.
      </p>
    );
  }

  const tMin = sorted[0].t;
  const tMax = sorted[sorted.length - 1].t;
  const yMin = Math.min(1.0, ...sorted.map((p) => p.y));
  const yMax = Math.max(1.2, ...sorted.map((p) => p.y)) * 1.05;

  const plotW = WIDTH - PAD_LEFT - PAD_RIGHT;
  const plotH = HEIGHT - PAD_TOP - PAD_BOTTOM;

  const xScale = (t: number) => PAD_LEFT + ((t - tMin) / (tMax - tMin || 1)) * plotW;
  const yScale = (y: number) => PAD_TOP + (1 - (y - yMin) / (yMax - yMin || 1)) * plotH;

  const linePath = sorted.map((p, i) => `${i === 0 ? "M" : "L"}${xScale(p.t)},${yScale(p.y)}`).join(" ");
  const areaPath = `${linePath} L${xScale(tMax)},${PAD_TOP + plotH} L${xScale(tMin)},${PAD_TOP + plotH} Z`;

  const baselineY = yScale(1.0);
  const last = sorted[sorted.length - 1];

  function handleMove(e: React.PointerEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * WIDTH;
    const targetT = tMin + ((px - PAD_LEFT) / plotW) * (tMax - tMin);
    let nearest = 0;
    let best = Infinity;
    sorted.forEach((p, i) => {
      const d = Math.abs(p.t - targetT);
      if (d < best) {
        best = d;
        nearest = i;
      }
    });
    setHoverIdx(nearest);
  }

  const hover = hoverIdx !== null ? sorted[hoverIdx] : null;

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="w-full touch-none"
        onPointerMove={handleMove}
        onPointerLeave={() => setHoverIdx(null)}
        role="img"
        aria-label="Congestion ratio over the last 24 hours"
      >
        {/* baseline gridline at free-flow (1.0x) */}
        <line
          x1={PAD_LEFT}
          x2={WIDTH - PAD_RIGHT}
          y1={baselineY}
          y2={baselineY}
          stroke="var(--gridline)"
          strokeWidth={1}
        />
        <text x={PAD_LEFT} y={baselineY - 4} fontSize="9" fill="var(--text-muted)">
          free flow
        </text>

        <path d={areaPath} fill="var(--chart-line)" opacity={0.1} stroke="none" />
        <path d={linePath} fill="none" stroke="var(--chart-line)" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

        {/* end marker + direct label */}
        <circle cx={xScale(last.t)} cy={yScale(last.y)} r={4} fill="var(--chart-line)" stroke="var(--surface-1)" strokeWidth={2} />
        <text
          x={xScale(last.t)}
          y={yScale(last.y) - 8}
          fontSize="10"
          fontWeight={600}
          textAnchor="end"
          fill="var(--text-primary)"
        >
          {last.y.toFixed(2)}x
        </text>

        {/* x-axis endpoints */}
        <text x={PAD_LEFT} y={HEIGHT - 6} fontSize="9" fill="var(--text-muted)">
          {new Date(tMin).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
        </text>
        <text x={WIDTH - PAD_RIGHT} y={HEIGHT - 6} fontSize="9" textAnchor="end" fill="var(--text-muted)">
          {new Date(tMax).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
        </text>

        {hover && (
          <line
            x1={xScale(hover.t)}
            x2={xScale(hover.t)}
            y1={PAD_TOP}
            y2={PAD_TOP + plotH}
            stroke="var(--baseline)"
            strokeWidth={1}
          />
        )}
        {hover && (
          <circle cx={xScale(hover.t)} cy={yScale(hover.y)} r={4} fill="var(--chart-line)" stroke="var(--surface-1)" strokeWidth={2} />
        )}
      </svg>

      {hover && (
        <div
          className="pointer-events-none absolute top-0 -translate-x-1/2 rounded-md border border-[var(--border-hairline)] bg-[var(--surface-1)] px-2 py-1 text-xs shadow-sm"
          style={{ left: `${(xScale(hover.t) / WIDTH) * 100}%` }}
        >
          <p className="font-semibold text-[var(--text-primary)]">{hover.y.toFixed(2)}x travel time</p>
          <p className="text-[var(--text-muted)]">
            {new Date(hover.t).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
          </p>
        </div>
      )}
    </div>
  );
}
