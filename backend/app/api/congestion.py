from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import CongestionReading, Corridor
from app.schemas.schemas import CongestionReadingOut, CorridorOut, LiveCorridorStatus
from app.services.congestion_calculator import compute_congestion

router = APIRouter(prefix="/api", tags=["congestion"])

STALE_AFTER = timedelta(minutes=30)


def _to_reading_out(reading: CongestionReading) -> CongestionReadingOut:
    result = compute_congestion(
        reading.current_travel_time_s, reading.free_flow_travel_time_s, reading.road_closure
    )
    return CongestionReadingOut(
        corridor_id=reading.corridor_id,
        recorded_at=reading.recorded_at,
        current_speed_kmh=reading.current_speed_kmh,
        free_flow_speed_kmh=reading.free_flow_speed_kmh,
        current_travel_time_s=reading.current_travel_time_s,
        free_flow_travel_time_s=reading.free_flow_travel_time_s,
        confidence=reading.confidence,
        road_closure=reading.road_closure,
        congestion_ratio=result.congestion_ratio,
        severity=result.severity,
    )


@router.get("/corridors", response_model=list[CorridorOut])
def list_corridors(db: Session = Depends(get_db)) -> list[Corridor]:
    return list(db.scalars(select(Corridor)))


@router.get("/congestion/live", response_model=list[LiveCorridorStatus])
def live_congestion(db: Session = Depends(get_db)) -> list[LiveCorridorStatus]:
    corridors = list(db.scalars(select(Corridor)))
    now = datetime.now(timezone.utc)
    out: list[LiveCorridorStatus] = []
    for corridor in corridors:
        latest = db.scalars(
            select(CongestionReading)
            .where(CongestionReading.corridor_id == corridor.id)
            .order_by(CongestionReading.recorded_at.desc())
            .limit(1)
        ).first()
        reading_out = _to_reading_out(latest) if latest else None
        stale = latest is None or (now - latest.recorded_at) > STALE_AFTER
        out.append(
            LiveCorridorStatus(
                corridor=CorridorOut.model_validate(corridor),
                latest_reading=reading_out,
                stale=stale,
            )
        )
    return out


@router.get("/congestion/history", response_model=list[CongestionReadingOut])
def congestion_history(
    corridor_id: str = Query(...),
    hours: int = Query(24, ge=1, le=24 * 30),
    db: Session = Depends(get_db),
) -> list[CongestionReadingOut]:
    corridor = db.get(Corridor, corridor_id)
    if corridor is None:
        raise HTTPException(status_code=404, detail=f"Unknown corridor_id '{corridor_id}'")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    readings = db.scalars(
        select(CongestionReading)
        .where(CongestionReading.corridor_id == corridor_id, CongestionReading.recorded_at >= since)
        .order_by(CongestionReading.recorded_at.asc())
    )
    return [_to_reading_out(r) for r in readings]
