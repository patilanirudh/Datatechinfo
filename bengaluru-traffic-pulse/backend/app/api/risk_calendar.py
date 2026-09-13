from datetime import date

from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.schemas.schemas import RiskDay
from app.services.risk_engine import build_risk_calendar, load_events

router = APIRouter(prefix="/api", tags=["risk-calendar"])


@router.get("/risk-calendar", response_model=list[RiskDay])
def risk_calendar(days: int = Query(60, ge=1, le=180)) -> list[RiskDay]:
    settings = get_settings()
    events = load_events(settings.events_calendar_file)
    assessments = build_risk_calendar(events, start=date.today(), days=days)
    return [
        RiskDay(
            date=a.the_date.isoformat(),
            risk_level=a.risk_level,
            score=a.score,
            reasons=a.reasons,
            recommendation=a.recommendation,
            related_event=a.related_event,
        )
        for a in assessments
    ]
