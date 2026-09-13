"""Polls TomTom's Incident Details API for a bounding box around the monitored
corridors and upserts each incident. TomTom's free Incident Details quota is only
2.5K/month, so this should run less often than poll_congestion.py (see
.github/workflows/ingest.yml)."""

import hashlib
import json
import logging
from datetime import datetime, timezone

import _bootstrap  # noqa: F401
from app.core.config import get_settings
from app.core.db import SessionLocal, init_db
from app.models import Incident
from app.services.tomtom_client import TomTomError, fetch_incidents

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("poll_incidents")

BBOX_BUFFER_DEGREES = 0.02


def _corridor_bbox(corridors: list[dict]) -> tuple[float, float, float, float]:
    lats = [c["lat"] for c in corridors]
    lons = [c["lon"] for c in corridors]
    return (
        min(lons) - BBOX_BUFFER_DEGREES,
        min(lats) - BBOX_BUFFER_DEGREES,
        max(lons) + BBOX_BUFFER_DEGREES,
        max(lats) + BBOX_BUFFER_DEGREES,
    )


def _first_coordinate(geometry: dict) -> tuple[float, float]:
    """Returns (lat, lon) from a GeoJSON-ish geometry; TomTom uses [lon, lat] ordering."""
    coords = geometry.get("coordinates", [])
    point = coords
    while isinstance(point, list) and point and isinstance(point[0], list):
        point = point[0]
    if isinstance(point, list) and len(point) >= 2:
        lon, lat = point[0], point[1]
        return float(lat), float(lon)
    return 0.0, 0.0


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> None:
    settings = get_settings()
    if not settings.tomtom_api_key:
        logger.error("TOMTOM_API_KEY is not set; aborting poll")
        raise SystemExit(1)

    init_db()

    with open(settings.corridors_file, encoding="utf-8") as f:
        corridors = json.load(f)["corridors"]
    bbox = _corridor_bbox(corridors)

    try:
        incidents = fetch_incidents(bbox, settings.tomtom_api_key)
    except TomTomError as exc:
        logger.error("incidentDetails poll failed: %s", exc)
        raise SystemExit(1) from exc

    db = SessionLocal()
    try:
        for feature in incidents:
            props = feature.get("properties", {})
            events = props.get("events") or [{}]
            description = events[0].get("description", "")
            lat, lon = _first_coordinate(feature.get("geometry", {}))
            start_time = _parse_time(props.get("startTime"))

            incident_id = hashlib.sha256(
                f"{description}|{props.get('startTime')}|{lat:.5f}|{lon:.5f}".encode()
            ).hexdigest()[:24]

            existing = db.get(Incident, incident_id)
            if existing is not None:
                # Still being reported by TomTom on this poll — refresh fetched_at so it keeps
                # counting as "active" (see api/incidents.py) instead of aging out between polls.
                existing.fetched_at = datetime.now(timezone.utc)
                existing.magnitude_of_delay = int(props.get("magnitudeOfDelay", 0) or 0)
                existing.end_time = _parse_time(props.get("endTime"))
                continue

            db.add(
                Incident(
                    id=incident_id,
                    description=description,
                    icon_category=str(props.get("iconCategory", "")),
                    magnitude_of_delay=int(props.get("magnitudeOfDelay", 0) or 0),
                    road_numbers=",".join(props.get("roadNumbers", []) or []),
                    start_time=start_time,
                    end_time=_parse_time(props.get("endTime")),
                    lat=lat,
                    lon=lon,
                )
            )
        db.commit()
    finally:
        db.close()

    logger.info("Fetched %d incidents in bbox %s", len(incidents), bbox)


if __name__ == "__main__":
    main()
