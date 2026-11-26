from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Query

from src.domains.algae_vision.schemas import AssessmentRequest
from src.domains.algae_vision.service import assess_category
from src.domains.haptan_monitor.repository import observation_repository
from src.domains.haptan_monitor.schemas import Observation, ObservationCreate

router = APIRouter(prefix="/api/v1/monitor", tags=["haptan-monitor"])


@router.post("/observations", response_model=Observation, status_code=201)
async def create_observation(request: ObservationCreate) -> Observation:
    assessment = assess_category(
        AssessmentRequest(
            algae_type=request.algae_type,
            confidence=request.confidence,
        )
    )
    observation = Observation(
        id=str(uuid4()),
        site_id=request.site_id,
        algae_type=request.algae_type,
        confidence=request.confidence,
        notes=request.notes,
        observed_at=datetime.now(timezone.utc),
        assessment_level=assessment.assessment_level,
        summary=assessment.summary,
    )
    observation_repository.create(observation)
    return observation


@router.get("/observations", response_model=list[Observation])
async def list_observations(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Observation]:
    return observation_repository.list_recent(limit)
