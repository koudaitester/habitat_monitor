from src.domains.algae_vision.features.profile import AlgaeProfile
from src.domains.algae_vision.schemas import AlgaeType

PROFILE = AlgaeProfile(
    algae_type=AlgaeType.CYANOBACTERIA,
    display_name="Cyanobacteria",
    assessment_level="review",
    summary="The submitted category is cyanobacteria.",
    recommendation="Review the observation and use appropriate sampling if a bloom is suspected.",
    caveat="This category does not establish species identity or toxin presence.",
)
