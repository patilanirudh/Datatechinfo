"use client";

import dynamic from "next/dynamic";
import type { LiveCorridorStatus } from "@/lib/types";

const CorridorMap = dynamic(() => import("./CorridorMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[420px] w-full animate-pulse rounded-lg bg-[var(--gridline)]" />
  ),
});

export default function CorridorMapClient({ corridors }: { corridors: LiveCorridorStatus[] }) {
  return <CorridorMap corridors={corridors} />;
}
