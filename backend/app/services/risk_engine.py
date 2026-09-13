"""Rule-based (not ML) risk calendar.

There is no training data yet to fit a model on, so this deliberately stays a
transparent, auditable set of rules derived from the Sep 11 2026 case study and
Karnataka's published holiday calendar. See data/case_study_sep11_2026.md and
data/events_calendar.csv for the underlying evidence. Once the live ingestion
pipeline (services/tomtom_client.py + ingestion/) has collected enough real
readings across several of these events, replacing this with a learned model
is the natural next step (see README roadmap) — not before.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


@dataclass(frozen=True)
class CalendarEvent:
    event_date: date
    name: str
    event_type: str
    evidenced_exodus: bool
    source_url: str
    notes: str


@dataclass(frozen=True)
class RiskAssessment:
    the_date: date
    risk_level: str
    score: int
    reasons: list[str] = field(default_factory=list)
    recommendation: str = ""
    related_event: str | None = None


def load_events(csv_path: Path) -> dict[date, CalendarEvent]:
    events: dict[date, CalendarEvent] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d = date.fromisoformat(row["date"])
            events[d] = CalendarEvent(
                event_date=d,
                name=row["name"],
                event_type=row["type"],
                evidenced_exodus=row["evidenced_exodus"].strip().lower() == "true",
                source_url=row["source_url"],
                notes=row.get("notes", ""),
            )
    return events


def is_second_or_fourth_saturday(d: date) -> bool:
    """Karnataka government holiday rule: 2nd and 4th Saturday of every month."""
    if d.weekday() != SATURDAY:
        return False
    week_of_month = (d.day - 1) // 7 + 1
    return week_of_month in (2, 4)


def is_non_working_day(d: date, events: dict[date, CalendarEvent]) -> bool:
    if d.weekday() == SUNDAY:
        return True
    if is_second_or_fourth_saturday(d):
        return True
    if d in events:
        return True
    return False


def non_working_block(d: date, events: dict[date, CalendarEvent]) -> list[date]:
    """The contiguous non-working block associated with `d`: the block containing `d` if
    `d` itself is non-working, otherwise the block `d` immediately launches into (e.g. a
    working Friday right before a festival weekend). Empty list if neither applies."""
    if is_non_working_day(d, events):
        start = d
        while is_non_working_day(start - timedelta(days=1), events):
            start -= timedelta(days=1)
        end = d
        while is_non_working_day(end + timedelta(days=1), events):
            end += timedelta(days=1)
    else:
        start = d + timedelta(days=1)
        if not is_non_working_day(start, events):
            return []
        end = start
        while is_non_working_day(end + timedelta(days=1), events):
            end += timedelta(days=1)

    block: list[date] = []
    cur = start
    while cur <= end:
        block.append(cur)
        cur += timedelta(days=1)
    return block


def long_weekend_length(d: date, events: dict[date, CalendarEvent]) -> int:
    """Length of the non-working block associated with `d` (see non_working_block)."""
    return len(non_working_block(d, events))


def assess_date(d: date, events: dict[date, CalendarEvent]) -> RiskAssessment:
    score = 0
    reasons: list[str] = []
    related_event: str | None = None

    block = non_working_block(d, events)
    block_events = [events[bd] for bd in block if bd in events]
    # Prefer an evidenced event over an un-evidenced one if a block spans several.
    best_event = max(block_events, key=lambda e: e.evidenced_exodus, default=None)
    if best_event is not None:
        related_event = best_event.name
        if best_event.evidenced_exodus:
            score += 60
            reasons.append(
                f"{best_event.name} on {best_event.event_date.isoformat()} — directly evidenced exodus pattern (see case study)"
            )
        else:
            score += 35
            reasons.append(
                f"{best_event.name} ({best_event.event_type}) on {best_event.event_date.isoformat()} "
                "— festival/holiday, exodus plausible by analogy"
            )

    if is_second_or_fourth_saturday(d):
        score += 20
        reasons.append("2nd/4th Saturday — standard Karnataka government holiday")

    break_len = len(block)
    if break_len >= 3:
        score += 25
        reasons.append(f"Part of/launches a {break_len}-day non-working block")
    elif break_len == 2:
        score += 10
        reasons.append("Part of/launches a 2-day weekend-adjacent block")

    if d.weekday() == FRIDAY and break_len >= 2:
        score += 10
        reasons.append("Friday before a multi-day break — evidenced exodus onset ~5PM in the case study")

    if score >= 80:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    if level in ("HIGH", "CRITICAL"):
        recommendation = (
            "Leave before 2 PM or after 11 PM if possible. Avoid Tumkur Rd, Mysore Rd, "
            "Kanakapura Rd and Hosur Rd between 5 PM-11 PM — these gridlocked in the Sep 11 2026 "
            "case study. Book buses/trains in advance; fares surge and seats sell out under this pattern."
        )
    elif level == "MEDIUM":
        recommendation = "Some elevated risk of holiday-adjacent congestion — check live corridor status before departing."
    else:
        recommendation = "No elevated risk detected from the holiday calendar for this date."

    return RiskAssessment(
        the_date=d,
        risk_level=level,
        score=score,
        reasons=reasons,
        recommendation=recommendation,
        related_event=related_event,
    )


def build_risk_calendar(events: dict[date, CalendarEvent], start: date, days: int = 60) -> list[RiskAssessment]:
    return [assess_date(start + timedelta(days=i), events) for i in range(days)]
