from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Corridor(Base):
    __tablename__ = "corridors"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String, default="")

    readings: Mapped[list["CongestionReading"]] = relationship(back_populates="corridor")


class CongestionReading(Base):
    __tablename__ = "congestion_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    corridor_id: Mapped[str] = mapped_column(ForeignKey("corridors.id"), index=True, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    current_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    free_flow_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    current_travel_time_s: Mapped[int] = mapped_column(Integer, nullable=False)
    free_flow_travel_time_s: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    road_closure: Mapped[bool] = mapped_column(Boolean, default=False)

    corridor: Mapped["Corridor"] = relationship(back_populates="readings")


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
    description: Mapped[str] = mapped_column(String, default="")
    icon_category: Mapped[str] = mapped_column(String, default="")
    magnitude_of_delay: Mapped[int] = mapped_column(Integer, default=0)
    road_numbers: Mapped[str] = mapped_column(String, default="")
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lon: Mapped[float] = mapped_column(Float, default=0.0)
