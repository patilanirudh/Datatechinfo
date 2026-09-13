from datetime import datetime

from pydantic import BaseModel


class CorridorOut(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    direction: str

    model_config = {"from_attributes": True}


class CongestionReadingOut(BaseModel):
    corridor_id: str
    recorded_at: datetime
    current_speed_kmh: float
    free_flow_speed_kmh: float
    current_travel_time_s: int
    free_flow_travel_time_s: int
    confidence: float
    road_closure: bool
    congestion_ratio: float
    severity: str

    model_config = {"from_attributes": True}


class LiveCorridorStatus(BaseModel):
    corridor: CorridorOut
    latest_reading: CongestionReadingOut | None
    stale: bool


class IncidentOut(BaseModel):
    id: str
    description: str
    icon_category: str
    magnitude_of_delay: int
    road_numbers: str
    start_time: datetime | None
    end_time: datetime | None
    lat: float
    lon: float

    model_config = {"from_attributes": True}


class RiskDay(BaseModel):
    date: str
    risk_level: str
    score: int
    reasons: list[str]
    recommendation: str
    related_event: str | None = None


class LocationSearchResult(BaseModel):
    query: str
    freeform_address: str
    lat: float
    lon: float
    current_speed_kmh: float
    free_flow_speed_kmh: float
    congestion_ratio: float
    severity: str
