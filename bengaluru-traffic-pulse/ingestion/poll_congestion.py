"""Polls TomTom's Flow Segment Data API for every corridor in data/corridors.json
and writes one CongestionReading row per corridor. Meant to be run on a schedule
(see .github/workflows/ingest.yml) — every invocation is a single, independent poll,
not a long-running process, so it survives running on ephemeral CI runners."""

import json
import logging

import _bootstrap  # noqa: F401  (must run before the app.* imports below)
from app.core.config import get_settings
from app.core.db import SessionLocal, init_db
from app.models import CongestionReading
from app.services.seed import seed_corridors
from app.services.tomtom_client import TomTomError, fetch_flow_segment

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("poll_congestion")


def main() -> None:
    settings = get_settings()
    if not settings.tomtom_api_key:
        logger.error("TOMTOM_API_KEY is not set; aborting poll")
        raise SystemExit(1)

    init_db()
    seed_corridors(settings.corridors_file)

    with open(settings.corridors_file, encoding="utf-8") as f:
        corridors = json.load(f)["corridors"]

    db = SessionLocal()
    ok, failed = 0, 0
    try:
        for c in corridors:
            try:
                flow = fetch_flow_segment(c["lat"], c["lon"], settings.tomtom_api_key)
            except TomTomError as exc:
                logger.warning("Skipping corridor %s: %s", c["id"], exc)
                failed += 1
                continue

            db.add(
                CongestionReading(
                    corridor_id=c["id"],
                    current_speed_kmh=flow.get("currentSpeed", 0),
                    free_flow_speed_kmh=flow.get("freeFlowSpeed", 0),
                    current_travel_time_s=flow.get("currentTravelTime", 0),
                    free_flow_travel_time_s=flow.get("freeFlowTravelTime", 0),
                    confidence=flow.get("confidence", 0.0),
                    road_closure=flow.get("roadClosure", False),
                )
            )
            ok += 1
        db.commit()
    finally:
        db.close()

    logger.info("Polled %d corridors: %d ok, %d failed", len(corridors), ok, failed)
    if ok == 0 and corridors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
