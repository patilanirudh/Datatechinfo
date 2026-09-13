"""Turns raw TomTom flow-segment data into a congestion ratio + severity label.

This is our own scale (documented on the Methodology page), not a reproduction of
Bengaluru Traffic Police's queue-length-based severity scale, since we measure
speed/travel-time ratio, not physical queue length.
"""

from __future__ import annotations

from dataclasses import dataclass

SEVERITY_THRESHOLDS: list[tuple[float, str]] = [
    (1.15, "free_flow"),
    (1.5, "moderate"),
    (2.0, "high"),
    (float("inf"), "severe"),
]


@dataclass(frozen=True)
class CongestionResult:
    congestion_ratio: float
    severity: str


def compute_congestion(current_travel_time_s: int, free_flow_travel_time_s: int, road_closure: bool) -> CongestionResult:
    if road_closure:
        return CongestionResult(congestion_ratio=float("inf"), severity="closed")

    if free_flow_travel_time_s <= 0:
        return CongestionResult(congestion_ratio=1.0, severity="free_flow")

    ratio = current_travel_time_s / free_flow_travel_time_s
    for threshold, label in SEVERITY_THRESHOLDS:
        if ratio <= threshold:
            return CongestionResult(congestion_ratio=round(ratio, 3), severity=label)
    return CongestionResult(congestion_ratio=round(ratio, 3), severity="severe")
