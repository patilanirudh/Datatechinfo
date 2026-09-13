from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(REPO_ROOT / ".env"), extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/bengaluru_traffic"
    tomtom_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    corridors_file: Path = REPO_ROOT / "data" / "corridors.json"
    events_calendar_file: Path = REPO_ROOT / "data" / "events_calendar.csv"
    case_study_file: Path = REPO_ROOT / "data" / "case_study_sep11_2026.md"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
