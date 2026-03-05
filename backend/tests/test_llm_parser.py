import os
import sys
import unittest

# Prevent import-time RuntimeError in gemini_client
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers.llm import _parse_events_tolerant
from app.schemas.radiology import RadiologyEvent
from app.schemas.pathologies import PathologyEvent


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

    def test_pathology_biopsy_type_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "biopsy_type": "Fine needle aspiration (FNA)",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].biopsy_type, "fine_needle")
        self.assertEqual(raw_events[0]["biopsy_type"], "Fine needle aspiration (FNA)")
        self.assertEqual(len(issues), 0)

    def test_pathology_biopsy_type_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "biopsy_type": "completely_unknown_biopsy_kind",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].biopsy_type, "completely_unknown_biopsy_kind")
        self.assertEqual(raw_events[0]["biopsy_type"], "completely_unknown_biopsy_kind")
        self.assertEqual(len(issues), 0)

    def test_pathology_biopsied_lesion_type_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "biopsied_lesion_type": "totally_unknown_lesion_value",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].biopsied_lesion_type, "totally_unknown_lesion_value")
        self.assertEqual(raw_events[0]["biopsied_lesion_type"], "totally_unknown_lesion_value")
        self.assertEqual(len(issues), 0)

    def test_pathology_biopsied_lesion_type_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "biopsied_lesion_type": "Resektion von Metastasen",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].biopsied_lesion_type, "resection_of_metastases")
        self.assertEqual(raw_events[0]["biopsied_lesion_type"], "Resektion von Metastasen")
        self.assertEqual(len(issues), 0)

    def test_pathology_eortc_grade_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "eortc_response_grade": "Grade 2 (< 50% necrosis)",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].eortc_response_grade, "grade_b")
        self.assertEqual(raw_events[0]["eortc_response_grade"], "Grade 2 (< 50% necrosis)")
        self.assertEqual(len(issues), 0)

    def test_pathology_eortc_grade_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "eortc_response_grade": "rare_custom_grade",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].eortc_response_grade, "rare_custom_grade")
        self.assertEqual(raw_events[0]["eortc_response_grade"], "rare_custom_grade")
        self.assertEqual(len(issues), 0)

    def test_pathology_extent_of_necrosis_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "extent_of_necrosis": "71-80%",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].extent_of_necrosis, "71_to_80_percent")
        self.assertEqual(raw_events[0]["extent_of_necrosis"], "71-80%")
        self.assertEqual(len(issues), 0)

    def test_pathology_extent_of_necrosis_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "extent_of_necrosis": "patchy small necrosis",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].extent_of_necrosis, "patchy small necrosis")
        self.assertEqual(raw_events[0]["extent_of_necrosis"], "patchy small necrosis")
        self.assertEqual(len(issues), 0)

    def test_pathology_prior_treatment_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "prior_treatment": "Combined treatment",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].prior_treatment, "radiotherapy_and_chemotherapy")
        self.assertEqual(raw_events[0]["prior_treatment"], "Combined treatment")
        self.assertEqual(len(issues), 0)

    def test_pathology_prior_treatment_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "prior_treatment": "rare_custom_prior_treatment",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].prior_treatment, "rare_custom_prior_treatment")
        self.assertEqual(raw_events[0]["prior_treatment"], "rare_custom_prior_treatment")
        self.assertEqual(len(issues), 0)

    def test_pathology_prior_treatment_missing_defaults_to_unknown(self):
        raw = [
            {
                "patient_id": 1,
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].prior_treatment, "unknown")
        self.assertEqual(len(raw_events), 1)
        self.assertEqual(len(issues), 0)

    def test_pathology_report_status_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "ihc_performed_status": "Performed",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].ihc_performed_status, "yes")
        self.assertEqual(raw_events[0]["ihc_performed_status"], "Performed")
        self.assertEqual(len(issues), 0)

    def test_pathology_report_status_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "dna_performed_status": "rare_custom_status",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].dna_performed_status, "rare_custom_status")
        self.assertEqual(raw_events[0]["dna_performed_status"], "rare_custom_status")
        self.assertEqual(len(issues), 0)

    def test_pathology_judgment_of_surgical_margin_maps_before_fallback(self):
        raw = [
            {
                "patient_id": 1,
                "judgment_of_surgical_margin": "R2",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].judgment_of_surgical_margin, "r2_intralesional_margin")
        self.assertEqual(raw_events[0]["judgment_of_surgical_margin"], "R2")
        self.assertEqual(len(issues), 0)

    def test_pathology_judgment_of_surgical_margin_unmapped_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "judgment_of_surgical_margin": "rare_custom_margin",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].judgment_of_surgical_margin, "rare_custom_margin")
        self.assertEqual(raw_events[0]["judgment_of_surgical_margin"], "rare_custom_margin")
        self.assertEqual(len(issues), 0)

    def test_pathology_judgment_of_surgical_margin_r1_without_subtype_keeps_raw_text(self):
        raw = [
            {
                "patient_id": 1,
                "judgment_of_surgical_margin": "R1",
            }
        ]

        events, raw_events, issues = _parse_events_tolerant(raw, PathologyEvent)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].judgment_of_surgical_margin, "R1")
        self.assertEqual(raw_events[0]["judgment_of_surgical_margin"], "R1")
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
