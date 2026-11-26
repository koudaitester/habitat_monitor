from datetime import datetime

from pydantic import BaseModel, Field

from src.domains.algae_vision.schemas import AlgaeType


class ObservationCreate(BaseModel):
    site_id: str = Field(min_length=1, max_length=100)
    algae_type: AlgaeType
    confidence: float = Field(ge=0, le=1)
    notes: str | None = Field(default=None, max_length=2000)


class Observation(ObservationCreate):
    id: str
    observed_at: datetime
    assessment_level: str
    summary: str
