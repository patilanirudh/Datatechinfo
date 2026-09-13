"use client";

import dynamic from "next/dynamic";
import type { LiveCorridorStatus, LocationSearchResult } from "@/lib/types";

const CorridorMap = dynamic(() => import("./CorridorMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[420px] w-full animate-pulse rounded-lg bg-[var(--gridline)]" />
  ),
});

export default function CorridorMapClient({
  corridors,
  searchMarker,
}: {
  corridors: LiveCorridorStatus[];
  searchMarker?: LocationSearchResult | null;
}) {
  return <CorridorMap corridors={corridors} searchMarker={searchMarker} />;
}
