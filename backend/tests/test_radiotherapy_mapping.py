import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.radioTherapy import RadiotherapyEvent


class TestRadiotherapyConstraintMapping(unittest.TestCase):
    def test_indications_map_and_keep_raw(self):
        event = RadiotherapyEvent(indications=["präoperativ", "custom indication"])
        self.assertEqual(event.indications, ["preoperative", "custom indication"])

    def test_therapy_types_map_and_keep_raw(self):
        event = RadiotherapyEvent(therapy_types=["IMRT", "unknown type"])
        self.assertEqual(event.therapy_types, ["intensity_modulated_radiotherapy_imrt", "unknown type"])

    def test_hyperthermia_status_maps(self):
        event = RadiotherapyEvent(hyperthermia_status="geplant")
        self.assertEqual(event.hyperthermia_status, "yes_radiation_hyperthermia")

    def test_hyperthermia_status_missing_is_null(self):
        event = RadiotherapyEvent()
        self.assertIsNone(event.hyperthermia_status)


if __name__ == "__main__":
    unittest.main()
