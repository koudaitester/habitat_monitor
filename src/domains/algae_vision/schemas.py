from enum import Enum

from pydantic import BaseModel, Field


class AlgaeType(str, Enum):
    NORMAL_CHLORELLA = "normal_chlorella"
    DIATOM = "diatom"
    CYANOBACTERIA = "cyanobacteria"
    OTHER_HARMFUL_ALGAE = "other_harmful_algae"


class AssessmentRequest(BaseModel):
    algae_type: AlgaeType
    confidence: float = Field(ge=0, le=1)


class AssessmentResponse(BaseModel):
    algae_type: AlgaeType
    display_name: str
    assessment_level: str
    confidence: float
    summary: str
    recommendation: str
    caveat: str
