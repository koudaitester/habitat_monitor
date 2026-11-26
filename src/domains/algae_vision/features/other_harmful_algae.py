from src.domains.algae_vision.features.profile import AlgaeProfile
from src.domains.algae_vision.schemas import AlgaeType

PROFILE = AlgaeProfile(
    algae_type=AlgaeType.OTHER_HARMFUL_ALGAE,
    display_name="Other harmful algae",
    assessment_level="attention",
    summary="The submitted category is other harmful algae.",
    recommendation="Escalate for expert or laboratory confirmation before making operational decisions.",
    caveat="The harmful-algae label is supplied by the caller and does not confirm a species or toxin.",
)
