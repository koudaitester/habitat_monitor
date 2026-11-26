from src.domains.algae_vision.features import PROFILES
from src.domains.algae_vision.schemas import (
    AssessmentRequest,
    AssessmentResponse,
)


def assess_category(request: AssessmentRequest) -> AssessmentResponse:
    profile = PROFILES[request.algae_type]
    return AssessmentResponse(
        algae_type=profile.algae_type,
        display_name=profile.display_name,
        assessment_level=profile.assessment_level,
        confidence=request.confidence,
        summary=profile.summary,
        recommendation=profile.recommendation,
        caveat=profile.caveat,
    )
