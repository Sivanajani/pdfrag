import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date

from app.schemas.radioTherapy import RadiotherapyEvent


class TestRadiotherapyDateParsing(unittest.TestCase):
    def test_four_digit_year(self):
        event = RadiotherapyEvent(therapy_start_date="15.01.2024")
        self.assertEqual(event.therapy_start_date, date(2024, 1, 15))

    def test_two_digit_year(self):
        event = RadiotherapyEvent(therapy_start_date="12.01.25")
        self.assertEqual(event.therapy_start_date, date(2025, 1, 12))

    def test_two_digit_year_end_date(self):
        event = RadiotherapyEvent(therapy_end_date="26.02.26")
        self.assertEqual(event.therapy_end_date, date(2026, 2, 26))

    def test_iso_format(self):
        event = RadiotherapyEvent(therapy_start_date="2025-01-12")
        self.assertEqual(event.therapy_start_date, date(2025, 1, 12))

    def test_date_range_from_llm_output(self):
        """LLM should split 'Therapieonkologie 12.01.25–26.02.26' into two fields."""
        event = RadiotherapyEvent(
            therapy_start_date="2025-01-12",
            therapy_end_date="2026-02-26",
        )
        self.assertEqual(event.therapy_start_date, date(2025, 1, 12))
        self.assertEqual(event.therapy_end_date, date(2026, 2, 26))

    def test_null_when_empty(self):
        event = RadiotherapyEvent(therapy_start_date=None)
        self.assertIsNone(event.therapy_start_date)


class TestRadiotherapyTherapyTypeMapping(unittest.TestCase):
    def test_uhrt_preserved_as_raw(self):
        event = RadiotherapyEvent(therapy_types=["uhRT"])
        self.assertEqual(event.therapy_types, ["uhRT"])

    def test_uhrt_lowercase_preserved_as_raw(self):
        event = RadiotherapyEvent(therapy_types=["uhrt"])
        self.assertEqual(event.therapy_types, ["uhrt"])

    def test_uh_dash_rt_preserved_as_raw(self):
        event = RadiotherapyEvent(therapy_types=["uh-RT"])
        self.assertEqual(event.therapy_types, ["uh-RT"])

    def test_ultrahypofraktioniert_preserved_as_raw(self):
        event = RadiotherapyEvent(therapy_types=["ultrahypofraktioniert"])
        self.assertEqual(event.therapy_types, ["ultrahypofraktioniert"])

    def test_chart_maps_to_conventional_3d(self):
        event = RadiotherapyEvent(therapy_types=["CHART"])
        self.assertEqual(event.therapy_types, ["conventional_3d"])

    def test_normofraktioniert_maps_to_conventional_3d(self):
        event = RadiotherapyEvent(therapy_types=["normofraktioniert"])
        self.assertEqual(event.therapy_types, ["conventional_3d"])

    def test_normofractionated_maps_to_conventional_3d(self):
        event = RadiotherapyEvent(therapy_types=["normofractionated"])
        self.assertEqual(event.therapy_types, ["conventional_3d"])

    def test_sbrt_still_stereotactic(self):
        event = RadiotherapyEvent(therapy_types=["SBRT"])
        self.assertEqual(event.therapy_types, ["stereotactic_radiotherapy"])

    def test_unknown_type_preserved_as_raw(self):
        event = RadiotherapyEvent(therapy_types=["SomeUnknownRT"])
        self.assertEqual(event.therapy_types, ["SomeUnknownRT"])


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
