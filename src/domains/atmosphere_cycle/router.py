from fastapi import APIRouter, Query

from src.domains.atmosphere_cycle.repository import atmosphere_repository
from src.domains.atmosphere_cycle.schemas import (
    AtmosphereReading,
    AtmosphereReadingCreate,
    AtmosphereStatus,
)
from src.domains.atmosphere_cycle.service import create_reading, get_status

router = APIRouter(prefix="/api/v1/atmosphere-cycle", tags=["atmosphere-cycle"])


@router.post("/readings", response_model=AtmosphereReading, status_code=201)
async def submit_reading(payload: AtmosphereReadingCreate) -> AtmosphereReading:
    return create_reading(payload)


@router.get("/status", response_model=AtmosphereStatus)
async def atmosphere_status() -> AtmosphereStatus:
    return get_status()


@router.get("/readings", response_model=list[AtmosphereReading])
async def list_readings(
    limit: int = Query(default=30, ge=1, le=100),
) -> list[AtmosphereReading]:
    return atmosphere_repository.list_recent(limit)
