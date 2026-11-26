from dataclasses import dataclass
from typing import Literal

from src.domains.algae_vision.schemas import AlgaeType


AssessmentLevel = Literal["informational", "review", "attention"]


@dataclass(frozen=True)
class AlgaeProfile:
    algae_type: AlgaeType
    display_name: str
    assessment_level: AssessmentLevel
    summary: str
    recommendation: str
    caveat: str
