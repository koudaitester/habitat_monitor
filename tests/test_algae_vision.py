import unittest

from src.domains.algae_vision.schemas import AlgaeType, AssessmentRequest
from src.domains.algae_vision.service import assess_category


class AlgaeVisionTests(unittest.TestCase):
    def test_assessments_cover_each_configured_category(self):
        for algae_type in AlgaeType:
            with self.subTest(algae_type=algae_type):
                result = assess_category(
                    AssessmentRequest(algae_type=algae_type, confidence=0.8)
                )
                self.assertEqual(result.algae_type, algae_type)
                self.assertTrue(result.display_name)
                self.assertEqual(result.confidence, 0.8)

    def test_harmful_category_is_flagged_for_review(self):
        result = assess_category(
            AssessmentRequest(
                algae_type=AlgaeType.OTHER_HARMFUL_ALGAE,
                confidence=0.95,
            )
        )
        self.assertEqual(result.assessment_level, "attention")
        self.assertIn("supplied by the caller", result.caveat)


if __name__ == "__main__":
    unittest.main()
