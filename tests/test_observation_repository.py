import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.domains.algae_vision.schemas import AlgaeType
from src.domains.haptan_monitor.repository import ObservationRepository
from src.domains.haptan_monitor.schemas import Observation


class ObservationRepositoryTests(unittest.TestCase):
    def test_observations_are_persisted_and_returned_newest_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = ObservationRepository(
                Path(temp_dir) / "data" / "observations.sqlite3"
            )
            repository.initialize()
            older = Observation(
                id="older",
                site_id="pond-1",
                algae_type=AlgaeType.DIATOM,
                confidence=0.7,
                observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                assessment_level="review",
                summary="Older observation",
            )
            newer = older.model_copy(
                update={
                    "id": "newer",
                    "observed_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
                }
            )
            repository.create(older)
            repository.create(newer)

            results = repository.list_recent(limit=1)

            self.assertEqual([item.id for item in results], ["newer"])
            self.assertEqual(results[0].assessment_level, "review")


if __name__ == "__main__":
    unittest.main()
