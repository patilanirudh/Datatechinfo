from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import case_study, congestion, incidents, risk_calendar, solutions
from app.core.config import get_settings
from app.core.db import init_db
from app.services.seed import seed_corridors

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    seed_corridors(settings.corridors_file)
    yield


app = FastAPI(
    title="Bengaluru Traffic Pulse",
    description="Root-cause analysis and live congestion tracking for Bengaluru's recurring festival-weekend gridlock.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(congestion.router)
app.include_router(incidents.router)
app.include_router(risk_calendar.router)
app.include_router(case_study.router)
app.include_router(solutions.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
