from src.domains.algae_vision.features.profile import AlgaeProfile
from src.domains.algae_vision.schemas import AlgaeType

PROFILE = AlgaeProfile(
    algae_type=AlgaeType.DIATOM,
    display_name="Diatom",
    assessment_level="review",
    summary="The submitted category is diatom.",
    recommendation="Review the observation in context; this broad group alone does not establish a hazard.",
    caveat="The category is supplied by the caller; species identification and risk need separate validation.",
)
