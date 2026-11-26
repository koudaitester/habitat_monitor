from fastapi import APIRouter

from src.domains.algae_vision.schemas import AssessmentRequest, AssessmentResponse
from src.domains.algae_vision.service import assess_category

router = APIRouter(prefix="/api/v1/algae-vision", tags=["algae-vision"])


@router.post("/assess", response_model=AssessmentResponse)
async def assess_algae(request: AssessmentRequest) -> AssessmentResponse:
    return assess_category(request)
