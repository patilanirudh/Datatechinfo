from datetime import date
from pathlib import Path

from app.services.risk_engine import (
    CalendarEvent,
    assess_date,
    is_second_or_fourth_saturday,
    load_events,
    long_weekend_length,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_EVENTS_CSV = REPO_ROOT / "data" / "events_calendar.csv"


def test_second_and_fourth_saturday_true():
    assert is_second_or_fourth_saturday(date(2026, 9, 12))  # confirmed 2nd Saturday, per case study
    assert is_second_or_fourth_saturday(date(2026, 9, 26))  # 4th Saturday of Sep 2026


def test_first_and_third_saturday_false():
    assert not is_second_or_fourth_saturday(date(2026, 9, 5))
    assert not is_second_or_fourth_saturday(date(2026, 9, 19))


def test_non_saturday_is_never_flagged():
    assert not is_second_or_fourth_saturday(date(2026, 9, 14))  # a Monday


def test_long_weekend_length_around_ganesh_chaturthi_2026():
    events = {date(2026, 9, 14): CalendarEvent(date(2026, 9, 14), "Ganesh Chaturthi", "festival", True, "", "")}
    # Fri Sep 11 (working) -> Sat 12 (2nd Sat, non-working) -> Sun 13 (non-working) -> Mon 14 (event, non-working)
    assert long_weekend_length(date(2026, 9, 11), events) == 3
    assert long_weekend_length(date(2026, 9, 13), events) == 3


def test_long_weekend_length_zero_for_isolated_working_day():
    assert long_weekend_length(date(2026, 9, 8), {}) == 0  # a Tuesday with no adjacent break


def test_assess_date_sep_11_2026_is_high_or_critical():
    events = {date(2026, 9, 14): CalendarEvent(date(2026, 9, 14), "Ganesh Chaturthi", "festival", True, "", "")}
    result = assess_date(date(2026, 9, 11), events)
    assert result.risk_level in ("HIGH", "CRITICAL")
    assert any("Friday" in r for r in result.reasons)


def test_assess_date_ordinary_tuesday_is_low():
    result = assess_date(date(2026, 9, 8), {})
    assert result.risk_level == "LOW"


def test_real_events_calendar_loads_and_flags_ganesh_chaturthi():
    events = load_events(REAL_EVENTS_CSV)
    gc = events[date(2026, 9, 14)]
    assert gc.evidenced_exodus is True
    assert "asianetnews" in gc.source_url
