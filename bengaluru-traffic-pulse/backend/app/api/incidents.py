from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Incident
from app.schemas.schemas import IncidentOut

router = APIRouter(prefix="/api", tags=["incidents"])

# Incident polling runs every 3h (see .github/workflows/ingest.yml) and re-fetched incidents
# have their fetched_at refreshed (see ingestion/poll_incidents.py), so this proxies "currently
# active" as "seen within the last poll cycle" with buffer for a missed/delayed run.
STALE_AFTER = timedelta(hours=4)


@router.get("/incidents/active", response_model=list[IncidentOut])
def active_incidents(db: Session = Depends(get_db)) -> list[Incident]:
    """Incidents whose most recent ingestion sighting falls within the last poll cycle — a
    proxy for 'currently active' since we don't track TomTom's own incident lifecycle."""
    since = datetime.now(timezone.utc) - STALE_AFTER
    return list(
        db.scalars(
            select(Incident)
            .where(Incident.fetched_at >= since)
            .order_by(Incident.magnitude_of_delay.desc())
        )
    )
