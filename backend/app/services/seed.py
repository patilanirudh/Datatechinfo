import json
from pathlib import Path

from app.core.db import SessionLocal
from app.models import Corridor


def seed_corridors(corridors_file: Path) -> None:
    with open(corridors_file, encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    try:
        for c in data["corridors"]:
            existing = db.get(Corridor, c["id"])
            if existing is None:
                db.add(
                    Corridor(
                        id=c["id"],
                        name=c["name"],
                        lat=c["lat"],
                        lon=c["lon"],
                        direction=c["direction"],
                    )
                )
        db.commit()
    finally:
        db.close()
