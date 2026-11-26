from src.domains.algae_vision.features.cyanobacteria import PROFILE as CYANOBACTERIA
from src.domains.algae_vision.features.diatom import PROFILE as DIATOM
from src.domains.algae_vision.features.normal_chlorella import (
    PROFILE as NORMAL_CHLORELLA,
)
from src.domains.algae_vision.features.other_harmful_algae import (
    PROFILE as OTHER_HARMFUL_ALGAE,
)

PROFILES = {
    profile.algae_type: profile
    for profile in (
        NORMAL_CHLORELLA,
        DIATOM,
        CYANOBACTERIA,
        OTHER_HARMFUL_ALGAE,
    )
}
