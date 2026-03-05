import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.pathologies import PathologyEvent, BiologicalBarrier


class TestPathologyBiologicalBarrierMapping(unittest.TestCase):
    def test_missing_barrier_defaults_to_none(self):
        event = PathologyEvent()
        self.assertEqual(event.biological_barrier_to_closest_margin, BiologicalBarrier.none)

    def test_blank_barrier_defaults_to_none(self):
        event = PathologyEvent(biological_barrier_to_closest_margin="  ")
        self.assertEqual(event.biological_barrier_to_closest_margin, BiologicalBarrier.none)

    def test_synonym_maps_to_fascia(self):
        event = PathologyEvent(biological_barrier_to_closest_margin="Faszie")
        self.assertEqual(event.biological_barrier_to_closest_margin, BiologicalBarrier.fascia)

    def test_na_maps_to_non_applicable(self):
        event = PathologyEvent(biological_barrier_to_closest_margin="N/A")
        self.assertEqual(event.biological_barrier_to_closest_margin, BiologicalBarrier.non_applicable)

    def test_unknown_value_goes_to_raw_text_comment(self):
        event = PathologyEvent(biological_barrier_to_closest_margin="my custom barrier")
        self.assertIsNone(event.biological_barrier_to_closest_margin)
        self.assertEqual(event.biological_barrier_to_closest_margin_comment, "raw_text: my custom barrier")

    def test_unknown_value_appends_to_existing_comment(self):
        event = PathologyEvent(
            biological_barrier_to_closest_margin="xyz barrier",
            biological_barrier_to_closest_margin_comment="from report",
        )
        self.assertIsNone(event.biological_barrier_to_closest_margin)
        self.assertEqual(
            event.biological_barrier_to_closest_margin_comment,
            "from report\nraw_text: xyz barrier",
        )

    def test_biopsied_lesion_type_uses_constraint_value_directly(self):
        event = PathologyEvent(biopsied_lesion_type="biopsy_of_metastases")
        self.assertEqual(event.biopsied_lesion_type, "biopsy_of_metastases")

    def test_biopsied_lesion_type_maps_legacy_value(self):
        event = PathologyEvent(biopsied_lesion_type="Primary tumor biopsy")
        self.assertEqual(event.biopsied_lesion_type, "biopsy_of_the_primary_tumor")

    def test_biopsied_lesion_type_maps_resection_synonym(self):
        event = PathologyEvent(biopsied_lesion_type="Resektion von Metastasen")
        self.assertEqual(event.biopsied_lesion_type, "resection_of_metastases")

    def test_biopsy_type_uses_constraint_value_directly(self):
        event = PathologyEvent(biopsy_type="core_biopsy")
        self.assertEqual(event.biopsy_type, "core_biopsy")

    def test_biopsy_type_maps_legacy_value(self):
        event = PathologyEvent(biopsy_type="Fine needle aspiration (FNA)")
        self.assertEqual(event.biopsy_type, "fine_needle")

    def test_biopsy_type_maps_incisional_without_suspicion(self):
        event = PathologyEvent(biopsy_type="Open incisional biopsy without suspicion")
        self.assertEqual(event.biopsy_type, "open_incisional_without_suspicion_of_sarcoma")

    def test_unmapped_biopsy_type_keeps_raw_text(self):
        event = PathologyEvent(biopsy_type="unmapped biopsy text")
        self.assertEqual(event.biopsy_type, "unmapped biopsy text")

    def test_unmapped_biopsied_lesion_type_keeps_raw_text(self):
        event = PathologyEvent(biopsied_lesion_type="unmapped lesion text")
        self.assertEqual(event.biopsied_lesion_type, "unmapped lesion text")

    def test_eortc_response_grade_uses_constraint_value_directly(self):
        event = PathologyEvent(eortc_response_grade="grade_c")
        self.assertEqual(event.eortc_response_grade, "grade_c")

    def test_eortc_response_grade_maps_legacy_value(self):
        event = PathologyEvent(eortc_response_grade="Grade 3 (50-90% necrosis)")
        self.assertEqual(event.eortc_response_grade, "grade_c")

    def test_eortc_response_grade_unmapped_keeps_raw_text(self):
        event = PathologyEvent(eortc_response_grade="unclear custom grade")
        self.assertEqual(event.eortc_response_grade, "unclear custom grade")

    def test_eortc_response_grade_missing_is_null(self):
        event = PathologyEvent()
        self.assertIsNone(event.eortc_response_grade)

    def test_extent_of_necrosis_uses_constraint_value_directly(self):
        event = PathologyEvent(extent_of_necrosis="31_to_40_percent")
        self.assertEqual(event.extent_of_necrosis, "31_to_40_percent")

    def test_extent_of_necrosis_maps_legacy_value(self):
        event = PathologyEvent(extent_of_necrosis="<10%")
        self.assertEqual(event.extent_of_necrosis, "less_than_10_percent")

    def test_extent_of_necrosis_unmapped_keeps_raw_text(self):
        event = PathologyEvent(extent_of_necrosis="focal necrosis present")
        self.assertEqual(event.extent_of_necrosis, "focal necrosis present")

    def test_extent_of_necrosis_missing_is_null(self):
        event = PathologyEvent()
        self.assertIsNone(event.extent_of_necrosis)

    def test_prior_treatment_uses_constraint_value_directly(self):
        event = PathologyEvent(prior_treatment="chemotherapy")
        self.assertEqual(event.prior_treatment, "chemotherapy")

    def test_prior_treatment_maps_legacy_value(self):
        event = PathologyEvent(prior_treatment="Combined treatment")
        self.assertEqual(event.prior_treatment, "radiotherapy_and_chemotherapy")

    def test_prior_treatment_unmapped_keeps_raw_text(self):
        event = PathologyEvent(prior_treatment="custom prior treatment text")
        self.assertEqual(event.prior_treatment, "custom prior treatment text")

    def test_prior_treatment_missing_is_null(self):
        event = PathologyEvent()
        self.assertEqual(event.prior_treatment, "unknown")

    def test_report_status_uses_constraint_value_directly(self):
        event = PathologyEvent(ihc_performed_status="not_yet_but_planned")
        self.assertEqual(event.ihc_performed_status, "not_yet_but_planned")

    def test_report_status_maps_legacy_value(self):
        event = PathologyEvent(fish_performed_status="Not performed")
        self.assertEqual(event.fish_performed_status, "no")

    def test_report_status_unmapped_keeps_raw_text(self):
        event = PathologyEvent(rna_performed_status="custom status text")
        self.assertEqual(event.rna_performed_status, "custom status text")

    def test_report_status_missing_is_null(self):
        event = PathologyEvent()
        self.assertIsNone(event.dna_performed_status)

    def test_judgment_of_surgical_margin_uses_constraint_value_directly(self):
        event = PathologyEvent(judgment_of_surgical_margin="r2_intralesional_margin")
        self.assertEqual(event.judgment_of_surgical_margin, "r2_intralesional_margin")

    def test_judgment_of_surgical_margin_maps_legacy_value(self):
        event = PathologyEvent(judgment_of_surgical_margin="R0 (complete resection, negative margins)")
        self.assertEqual(event.judgment_of_surgical_margin, "ro_wide_margin")

    def test_judgment_of_surgical_margin_unmapped_keeps_raw_text(self):
        event = PathologyEvent(judgment_of_surgical_margin="custom margin text")
        self.assertEqual(event.judgment_of_surgical_margin, "custom margin text")

    def test_judgment_of_surgical_margin_missing_is_null(self):
        event = PathologyEvent()
        self.assertIsNone(event.judgment_of_surgical_margin)


if __name__ == "__main__":
    unittest.main()
