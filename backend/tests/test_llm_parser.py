import os
import sys
import unittest

# Prevent import-time RuntimeError in gemini_client
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers.llm import _parse_events_tolerant
from app.schemas.radiology import RadiologyEvent


class TestLLMParserNoDataLoss(unittest.TestCase):
    def test_invalid_enum_is_reported_but_raw_is_preserved(self):
        raw = [
            {
                "exam_date": "2024-01-15",
                "location_of_lesion": "Oberarm",
                "largest_lesion_size_in_mm": 25,
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, RadiologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(len(raw_events), 1)
        self.assertEqual(raw_events[0]["location_of_lesion"], "Oberarm")
        self.assertIsNone(events[0].location_of_lesion)
        self.assertEqual(events[0].largest_lesion_size_in_mm, 25)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].field, "location_of_lesion")
        self.assertEqual(issues[0].raw_value, "Oberarm")

    def test_non_object_event_creates_issue(self):
        raw = ["not-an-object"]

        events, raw_events, issues = _parse_events_tolerant(raw, RadiologyEvent)

        self.assertEqual(events, [])
        self.assertEqual(raw_events, [])
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].raw_value, "not-an-object")


if __name__ == "__main__":
    unittest.main()
