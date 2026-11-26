from src.domains.algae_vision.features.profile import AlgaeProfile
from src.domains.algae_vision.schemas import AlgaeType

PROFILE = AlgaeProfile(
    algae_type=AlgaeType.NORMAL_CHLORELLA,
    display_name="Normal chlorella",
    assessment_level="informational",
    summary="The submitted category is normal chlorella.",
    recommendation="Continue routine monitoring and retain the sample record.",
    caveat="The category is supplied by the caller and has not been independently verified.",
)
