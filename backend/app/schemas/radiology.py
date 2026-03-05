from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class RadiologyExamType(str, Enum):
    conventional_x_ray = "conventional_x_ray"
    mri = "mri"
    ct_scan = "ct_scan"
    ultrasound = "ultrasound"
    pet_ct = "pet_ct"
    pet_mri = "pet_mri"
    scintigraphy = "scintigraphy"
    other = "other"


class TimingOfImaging(str, Enum):
    initial_imaging = "initial_imaging"
    post_neoadjuvant_pre_op = "post_neoadjuvant_pre_op"
    immediate_post_op_baseline_6_12_weeks = "immediate_post_op_baseline_6_12_weeks"
    surveillance = "surveillance"
    at_suspicion_of_local_recurrence = "at_suspicion_of_local_recurrence"
    at_suspicion_of_systemic_recurrence = "at_suspicion_of_systemic_recurrence"


class TypeOfImaging(str, Enum):
    local_imaging = "local_imaging"
    systemic_imaging = "systemic_imaging"


class LocationOfLesion(str, Enum):
    epifascial = "epifascial"
    subfascial = "subfascial"
    bone = "bone"


class RECISTResponse(str, Enum):
    not_applicable = "not_applicable"
    complete_remission_cr = "complete_remission_cr"
    partial_remission_pr = "partial_remission_pr"
    stable_disease_sd = "stable_disease_sd"
    progressive_disease_pd = "progressive_disease_pd"


class ChoiResponse(str, Enum):
    not_applicable = "not_applicable"
    complete_response_cr = "complete_response_cr"
    partial_response_pr = "partial_response_pr"
    stable_disease_sd = "stable_disease_sd"
    progressive_disease_pd = "progressive_disease_pd"


class iRECISTResponse(str, Enum):
    not_applicable = "not_applicable"
    complete_response_icr = "complete_response_icr"
    partial_response_ipr = "partial_response_ipr"
    stable_disease_isd = "stable_disease_isd"
    unconfirmed_progressive_iupd = "unconfirmed_progressive_iupd"
    confirmed_progression_icpd = "confirmed_progression_icpd"


class PETResponse(str, Enum):
    """For pet_response field (global PET response)"""
    not_applicable = "not_applicable"
    complete_metabolic_response_mcr = "complete_metabolic_response_mcr"
    partial_metabolic_response_pmr = "partial_metabolic_response_pmr"
    stable_metabolic_disease_smd = "stable_metabolic_disease_smd"
    progressive_metabolic_disease_pmd = "progressive_metabolic_disease_pmd"


class LocalPETResponse(str, Enum):
    """For local_disease_pet_metabolic_response field"""
    cmr = "cmr"
    pmr = "pmr"
    smd = "smd"
    pmd = "pmd"


class LocalDiseaseStatus(str, Enum):
    no_evidence_of_local_disease = "no_evidence_of_local_disease"
    residual_viable_local_tumor_suspected = "residual_viable_local_tumor_suspected"
    indeterminate_post_treatment_change = "indeterminate_post_treatment_change"
    local_recurrence_suspected = "local_recurrence_suspected"
    local_recurrence_confirmed = "local_recurrence_confirmed"


class QualitativeMRIResponse(str, Enum):
    likely_viable = "likely_viable"
    indeterminate = "indeterminate"
    likely_treatment_effect = "likely_treatment_effect"


class MetastasisStatus(str, Enum):
    no = "no"
    yes = "yes"
    indeterminate = "indeterminate"


class AnatomicLocationOfMetastasis(str, Enum):
    lung = "lung"
    pleura = "pleura"
    bone = "bone"
    liver = "liver"
    soft_tissue = "soft_tissue"
    lymph_node = "lymph_node"
    brain = "brain"
    other = "other"


class MetastasisCount(str, Enum):
    one = "one"
    two_to_five = "two_to_five"
    more_than_five = "more_than_five"


class MetastasisIndeterminateCategory(str, Enum):
    ipn_low = "ipn_low"
    ipn_indeterminate = "ipn_indeterminate"
    ipn_high = "ipn_high"
    unclear = "unclear"


class RadiologyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_radiology_exams Tabelle.
    Enthält alle Felder für vollständige Radiology-Befunde.
    """

    # IDs (in DB nicht nullable, aber hier optional für LLM-Extraktion)
    patient_id: Optional[int] = Field(default=None, ge=0)

    # Datum (optional — LLM liefert nicht immer ein Datum)
    exam_date: Optional[date] = Field(default=None, description="Untersuchungsdatum")

    # Grundlegende Untersuchungs-Informationen
    exam_type: Optional[str] = None
    exam_type_comment: Optional[str] = Field(default=None, max_length=2000)
    imaging_timing: Optional[str] = None
    imaging_type: Optional[str] = None

    # Läsions-Informationen
    location_of_lesion: Optional[str] = None
    largest_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)
    medium_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)
    smallest_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)

    # Response-Kriterien
    recist_response: Optional[str] = None
    choi_response: Optional[str] = None
    irecist_response: Optional[str] = None
    pet_response: Optional[str] = None

    # Lokale Erkrankung
    local_disease_status: Optional[str] = None
    local_disease_measurable: Optional[str] = None
    local_disease_report_largest_diameter: Optional[int] = Field(
        default=None,
        ge=0,
        description="Größter Durchmesser der lokalen Läsion in mm"
    )
    local_disease_qualitative_mri_response: Optional[str] = None
    local_disease_radiologist_confidence: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Radiologist confidence level (1-5)"
    )
    local_disease_pet_metabolic_response: Optional[str] = None

    # Metastasen - Allgemein
    metastasis_presence: Optional[bool] = Field(
        default=None,
        description="Metastasen vorhanden? (deprecated, use metastasis field)"
    )
    metastasis: Optional[str] = None
    anatomic_location_of_metastasis: List[str] = Field(
        default_factory=list,
        description="Anatomische Lokalisationen der Metastasen (Array)"
    )

    # Metastasen - Lokalisation mit Anzahl
    metastasis_location_lung_count: Optional[str] = None
    metastasis_location_pleura_count: Optional[str] = None
    metastasis_location_bone_count: Optional[str] = None
    metastasis_location_liver_count: Optional[str] = None
    metastasis_location_soft_tissue_count: Optional[str] = None
    metastasis_location_lymph_node_count: Optional[str] = None
    metastasis_location_brain_count: Optional[str] = None
    metastasis_location_other_count: Optional[str] = None

    # Metastasen - Messungen
    metastasis_target_lesion_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Anzahl der Target-Läsionen"
    )
    metastasis_longest_diameter_mm: Optional[int] = Field(
        default=None,
        ge=0,
        description="Längster Durchmesser der Metastasen in mm"
    )
    metastasis_indeterminate_category: Optional[str] = None

    # Befundtext und Datum
    radiology_report: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Vollständiger Radiologie-Befundtext"
    )
    report_date: Optional[date] = Field(default=None, description="Befunddatum")

    @staticmethod
    def _normalize_exam_type(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/exam_type.yml:
        conventional_x_ray, mri, ct_scan, ultrasound, pet_ct, pet_mri, scintigraphy, other
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()\[\]]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {"conventional_x_ray", "mri", "ct_scan", "ultrasound", "pet_ct", "pet_mri", "scintigraphy", "other"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Old enum / free text mappings
        if "pet-ct" in lower or "pet ct" in lower or "petct" in lower:
            return "pet_ct"
        if "pet-mri" in lower or "pet mri" in lower or "pet mrt" in lower or "petmrt" in lower:
            return "pet_mri"
        if any(token in lower for token in ["x-ray", "x ray", "xray", "röntgen", "roentgen", "conventional"]):
            return "conventional_x_ray"
        if any(token in lower for token in ["mrt", "mri", "magnetic resonance"]):
            return "mri"
        if any(token in lower for token in ["ct scan", "ct-scan", "computed tomography", "computertomograph"]):
            return "ct_scan"
        if lower.strip() == "ct":
            return "ct_scan"
        if any(token in lower for token in ["ultrasound", "ultraschall", "sonograph"]):
            return "ultrasound"
        if "us" == lower.strip():
            return "ultrasound"
        if any(token in lower for token in ["scintigraphy", "szintigraph", "bone scan"]):
            return "scintigraphy"
        if any(token in lower for token in ["other", "sonst", "ander"]):
            return "other"
        return raw

    @staticmethod
    def _normalize_imaging_timing(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/imaging_timing.yml:
        initial_imaging, post_neoadjuvant_pre_op, immediate_post_op_baseline_6_12_weeks,
        surveillance, at_suspicion_of_local_recurrence, at_suspicion_of_systemic_recurrence
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {
            "initial_imaging", "post_neoadjuvant_pre_op", "immediate_post_op_baseline_6_12_weeks",
            "surveillance", "at_suspicion_of_local_recurrence", "at_suspicion_of_systemic_recurrence",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Old enum / free text
        if any(token in lower for token in ["local recurrence", "lokalrezidiv"]) and "systemic" not in lower:
            return "at_suspicion_of_local_recurrence"
        if any(token in lower for token in ["systemic recurrence", "fernrezidiv", "fernmetastase"]):
            return "at_suspicion_of_systemic_recurrence"
        if any(token in lower for token in ["post_neoadjuvant", "post neoadjuvant", "nach neoadjuvant"]):
            return "post_neoadjuvant_pre_op"
        if any(token in lower for token in ["postop", "post_op", "post op", "immediate post", "6-12 weeks", "6 to 12"]):
            return "immediate_post_op_baseline_6_12_weeks"
        if any(token in lower for token in ["surveillance", "verlaufskontrolle", "follow-up", "follow up", "nachsorge"]):
            return "surveillance"
        if any(token in lower for token in ["initial", "erst", "first"]) and "post" not in lower:
            return "initial_imaging"
        return raw

    @staticmethod
    def _normalize_imaging_type(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/imaging_type.yml:
        local_imaging, systemic_imaging
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"local_imaging", "systemic_imaging"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["local", "lokal", "loko"]):
            return "local_imaging"
        if any(token in lower for token in ["systemic", "systemisch", "ganzkörper", "whole body"]):
            return "systemic_imaging"
        return raw

    @staticmethod
    def _normalize_location_of_lesion(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/location_of_lesion.yml:
        epifascial, subfascial, bone
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"epifascial", "subfascial", "bone"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["epifascial", "epifasziell", "oberflächlich", "superficial"]):
            return "epifascial"
        if any(token in lower for token in ["subfascial", "subfasziell", "tief", "deep", "intramuscular"]):
            return "subfascial"
        if any(token in lower for token in ["bone", "knochen", "ossär", "skelett"]):
            return "bone"
        return raw

    @staticmethod
    def _normalize_recist_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/recist_response.yml:
        not_applicable, complete_remission_cr, partial_remission_pr,
        stable_disease_sd, progressive_disease_pd
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()\[\]]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {"not_applicable", "complete_remission_cr", "partial_remission_pr", "stable_disease_sd", "progressive_disease_pd"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["n/a", "not applicable", "nicht zutreffend"]):
            return "not_applicable"
        if any(token in lower for token in ["progressive disease", "progression", "progress"]) or lower.strip() == "pd":
            return "progressive_disease_pd"
        if any(token in lower for token in ["stable disease", "stabile erkrankung", "stabil"]) or lower.strip() == "sd":
            return "stable_disease_sd"
        if any(token in lower for token in ["partial remission", "partial response", "partielle remission"]) or lower.strip() == "pr":
            return "partial_remission_pr"
        if any(token in lower for token in ["complete remission", "complete response", "komplette remission", "vollständige remission"]) or lower.strip() == "cr":
            return "complete_remission_cr"
        return raw

    @staticmethod
    def _normalize_choi_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/choi_response.yml:
        not_applicable, complete_response_cr, partial_response_pr,
        stable_disease_sd, progressive_disease_pd
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()\[\]]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {"not_applicable", "complete_response_cr", "partial_response_pr", "stable_disease_sd", "progressive_disease_pd"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["n/a", "not applicable"]):
            return "not_applicable"
        if any(token in lower for token in ["progressive disease", "progression", "progress"]) or lower.strip() == "pd":
            return "progressive_disease_pd"
        if any(token in lower for token in ["stable disease", "stabil"]) or lower.strip() == "sd":
            return "stable_disease_sd"
        if any(token in lower for token in ["partial response", "partial remission"]) or lower.strip() == "pr":
            return "partial_response_pr"
        if any(token in lower for token in ["complete response", "complete remission"]) or lower.strip() == "cr":
            return "complete_response_cr"
        return raw

    @staticmethod
    def _normalize_irecist_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/irecist_response.yml:
        not_applicable, complete_response_icr, partial_response_ipr, stable_disease_isd,
        unconfirmed_progressive_iupd, confirmed_progression_icpd
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()\[\]]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {
            "not_applicable", "complete_response_icr", "partial_response_ipr",
            "stable_disease_isd", "unconfirmed_progressive_iupd", "confirmed_progression_icpd",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["n/a", "not applicable"]):
            return "not_applicable"
        if any(token in lower for token in ["icpd", "confirmed progression"]):
            return "confirmed_progression_icpd"
        if any(token in lower for token in ["iupd", "unconfirmed", "nicht bestätigt"]):
            return "unconfirmed_progressive_iupd"
        if any(token in lower for token in ["icr", "immune complete", "icomplete"]) or lower.strip() == "icr":
            return "complete_response_icr"
        if any(token in lower for token in ["ipr", "immune partial"]) or lower.strip() == "ipr":
            return "partial_response_ipr"
        if any(token in lower for token in ["isd", "immune stable"]) or lower.strip() == "isd":
            return "stable_disease_isd"
        return raw

    @staticmethod
    def _normalize_pet_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/pet_response.yml:
        not_applicable, complete_metabolic_response_mcr, partial_metabolic_response_pmr,
        stable_metabolic_disease_smd, progressive_metabolic_disease_pmd
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.()\[\]]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {
            "not_applicable", "complete_metabolic_response_mcr", "partial_metabolic_response_pmr",
            "stable_metabolic_disease_smd", "progressive_metabolic_disease_pmd",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["n/a", "not applicable"]):
            return "not_applicable"
        if any(token in lower for token in ["pmd", "progressive metabolic"]):
            return "progressive_metabolic_disease_pmd"
        if any(token in lower for token in ["smd", "stable metabolic"]):
            return "stable_metabolic_disease_smd"
        if any(token in lower for token in ["pmr", "partial metabolic"]):
            return "partial_metabolic_response_pmr"
        if any(token in lower for token in ["cmr", "mcr", "complete metabolic"]):
            return "complete_metabolic_response_mcr"
        return raw

    @staticmethod
    def _normalize_local_disease_status(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/local_disease_status.yml:
        no_evidence_of_local_disease, residual_viable_local_tumor_suspected,
        indeterminate_post_treatment_change, local_recurrence_suspected,
        local_recurrence_confirmed
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {
            "no_evidence_of_local_disease", "residual_viable_local_tumor_suspected",
            "indeterminate_post_treatment_change", "local_recurrence_suspected",
            "local_recurrence_confirmed",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Old enum / free text
        if any(token in lower for token in ["recurrence confirmed", "bestätigt", "confirmed recurrence"]):
            return "local_recurrence_confirmed"
        if any(token in lower for token in ["recurrence suspected", "verdacht lokalrezidiv", "suspected recurrence"]):
            return "local_recurrence_suspected"
        if any(token in lower for token in ["no disease", "kein tumor", "no evidence", "ned"]):
            return "no_evidence_of_local_disease"
        if any(token in lower for token in ["residual", "resttumor", "viable"]):
            return "residual_viable_local_tumor_suspected"
        if any(token in lower for token in ["indeterminate", "unklar", "post treatment", "therapieeffekt"]):
            return "indeterminate_post_treatment_change"
        if any(token in lower for token in ["measurable", "messbar", "non-measurable", "non_measurable"]):
            return "residual_viable_local_tumor_suspected"
        return raw

    @staticmethod
    def _normalize_qualitative_mri_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/local_disease_qualitative_mri_response.yml:
        likely_viable, indeterminate, likely_treatment_effect
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"likely_viable", "indeterminate", "likely_treatment_effect"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["viable", "lebensfähig", "vitaler", "aktiver tumor", "progressive"]):
            return "likely_viable"
        if any(token in lower for token in ["indeterminate", "unklar", "unbestimmt"]):
            return "indeterminate"
        if any(token in lower for token in ["treatment effect", "therapieeffekt", "complete response", "partial response", "stable"]):
            return "likely_treatment_effect"
        return raw

    @staticmethod
    def _normalize_local_pet_response(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/local_disease_pet_metabolic_response.yml:
        cmr, pmr, smd, pmd
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"cmr", "pmr", "smd", "pmd"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["pmd", "progressive metabolic"]):
            return "pmd"
        if any(token in lower for token in ["smd", "stable metabolic"]):
            return "smd"
        if any(token in lower for token in ["pmr", "partial metabolic"]):
            return "pmr"
        if any(token in lower for token in ["cmr", "complete metabolic"]):
            return "cmr"
        return raw

    @staticmethod
    def _normalize_metastasis(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/metastasis.yml:
        "no", "yes", indeterminate
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()

        allowed = {"no", "yes", "indeterminate"}
        if lower in allowed:
            return lower

        if any(token in lower for token in ["no metastasis", "keine metastase", "metastasis free", "no evidence"]):
            return "no"
        if any(token in lower for token in ["metastasis present", "metastasen vorhanden", "ja"]):
            return "yes"
        if any(token in lower for token in ["indeterminate", "unklar", "fraglich"]):
            return "indeterminate"
        if lower in ("true", "yes", "1"):
            return "yes"
        if lower in ("false", "no", "nein", "0"):
            return "no"
        return raw

    @staticmethod
    def _normalize_anatomic_location(value) -> Optional[str]:
        """
        Normalisiert einen Eintrag in anatomic_location_of_metastasis.
        Constraint-Werte laut db/constraints/radiology_exam/anatomic_location_of_metastasis.yml:
        lung, pleura, bone, liver, soft_tissue, lymph_node, brain, other
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"lung", "pleura", "bone", "liver", "soft_tissue", "lymph_node", "brain", "other"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["lung", "lunge", "pulmon"]):
            return "lung"
        if any(token in lower for token in ["pleura", "pleural"]):
            return "pleura"
        if any(token in lower for token in ["bone", "knochen", "ossär", "skelett"]):
            return "bone"
        if any(token in lower for token in ["liver", "leber", "hepat"]):
            return "liver"
        if any(token in lower for token in ["soft tissue", "weichteil", "soft_tissue"]):
            return "soft_tissue"
        if any(token in lower for token in ["lymph node", "lymphknoten", "lymph_node"]):
            return "lymph_node"
        if any(token in lower for token in ["brain", "gehirn", "zerebral", "cranial", "hirn"]):
            return "brain"
        if any(token in lower for token in ["peritoneum", "peritoneal"]):
            return "other"  # peritoneum not in DB constraint → other
        if any(token in lower for token in ["other", "sonst", "ander"]):
            return "other"
        return raw

    @staticmethod
    def _normalize_metastasis_count(value) -> Optional[str]:
        """
        Normalisiert Anzahl-Werte auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/metastasis_location_count.yml:
        one, two_to_five, more_than_five
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {"one", "two_to_five", "more_than_five"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Parse numeric values from old enum or free text
        numbers = [int(x) for x in re.findall(r"\d+", raw)]
        if numbers:
            n = numbers[0]
            if n == 0:
                return None  # 0 = no metastasis in that location
            if n == 1:
                return "one"
            if 2 <= n <= 5:
                return "two_to_five"
            return "more_than_five"

        if any(token in lower for token in ["multiple", "numerous", "many", "viele", "zahlreich"]):
            return "more_than_five"
        if lower in ("one", "ein", "einen", "eine"):
            return "one"
        if any(token in lower for token in ["two", "three", "four", "five", "zwei", "drei", "vier", "fünf"]):
            return "two_to_five"
        return raw

    @staticmethod
    def _normalize_metastasis_indeterminate_category(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/radiology_exam/metastasis_indeterminate_category.yml:
        ipn_low, ipn_indeterminate, ipn_high, unclear
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"ipn_low", "ipn_indeterminate", "ipn_high", "unclear"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["probably benign", "wahrscheinlich benigne", "low risk", "niedrig"]):
            return "ipn_low"
        if any(token in lower for token in ["suspicious", "verdächtig", "high risk", "hoch"]):
            return "ipn_high"
        if any(token in lower for token in ["indeterminate", "unbestimmt"]):
            return "ipn_indeterminate"
        if any(token in lower for token in ["unclear", "unklar", "fraglich"]):
            return "unclear"
        return raw

    @model_validator(mode="before")
    @classmethod
    def normalize_radiology_fields(cls, data):
        if not isinstance(data, dict):
            return data

        # Single-value constrained fields
        for field, normalizer in [
            ("exam_type", cls._normalize_exam_type),
            ("imaging_timing", cls._normalize_imaging_timing),
            ("imaging_type", cls._normalize_imaging_type),
            ("location_of_lesion", cls._normalize_location_of_lesion),
            ("recist_response", cls._normalize_recist_response),
            ("choi_response", cls._normalize_choi_response),
            ("irecist_response", cls._normalize_irecist_response),
            ("pet_response", cls._normalize_pet_response),
            ("local_disease_status", cls._normalize_local_disease_status),
            ("local_disease_qualitative_mri_response", cls._normalize_qualitative_mri_response),
            ("local_disease_pet_metabolic_response", cls._normalize_local_pet_response),
            ("metastasis", cls._normalize_metastasis),
            ("metastasis_indeterminate_category", cls._normalize_metastasis_indeterminate_category),
        ]:
            raw = data.get(field)
            normalized = normalizer(raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None

        # local_disease_measurable — no constraint file, normalize yes/no/unknown
        measurable_raw = data.get("local_disease_measurable")
        if isinstance(measurable_raw, str):
            m = measurable_raw.strip().lower()
            if m in ("yes", "ja", "true", "1"):
                data["local_disease_measurable"] = "yes"
            elif m in ("no", "nein", "false", "0"):
                data["local_disease_measurable"] = "no"
            elif m in ("unknown", "unbekannt", "unklar", "n/a"):
                data["local_disease_measurable"] = "unknown"

        # Array: anatomic_location_of_metastasis
        raw_locations = data.get("anatomic_location_of_metastasis") or []
        if isinstance(raw_locations, list):
            normalized = []
            for v in raw_locations:
                n = cls._normalize_anatomic_location(v)
                if n is not None:
                    normalized.append(n)
            data["anatomic_location_of_metastasis"] = normalized

        # Metastasis count fields (all share same constraint)
        for field in (
            "metastasis_location_lung_count",
            "metastasis_location_pleura_count",
            "metastasis_location_bone_count",
            "metastasis_location_liver_count",
            "metastasis_location_soft_tissue_count",
            "metastasis_location_lymph_node_count",
            "metastasis_location_brain_count",
            "metastasis_location_other_count",
        ):
            raw = data.get(field)
            normalized = cls._normalize_metastasis_count(raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None

        # Konsistenzregel zwischen metastasis (no|yes|indeterminate) und metastasis_presence (bool|null)
        metastasis_value = data.get("metastasis")
        metastasis_presence = data.get("metastasis_presence")

        if metastasis_value == "yes":
            data["metastasis_presence"] = True
        elif metastasis_value == "no":
            data["metastasis_presence"] = False
        elif metastasis_value == "indeterminate":
            data["metastasis_presence"] = None
        elif metastasis_value is None or (isinstance(metastasis_value, str) and not metastasis_value.strip()):
            # Wenn metastasis nicht gesetzt ist, aus metastasis_presence ergänzen
            if metastasis_presence is True:
                data["metastasis"] = "yes"
            elif metastasis_presence is False:
                data["metastasis"] = "no"

        return data

    @field_validator("exam_date", "report_date", mode="before")
    @classmethod
    def parse_dates(cls, v):
        """
        Parst flexible Datumsformate (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
        """
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        if isinstance(v, date):
            return v

        if isinstance(v, str):
            s = v.strip()
            s = s.split(' ')[0]  # Entfernt Textanhänge
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class RadiologyEvents(BaseModel):
    """
    Wrapper für mehrere Radiologie-Events, extrahiert aus einem Bericht.
    """
    events: List[RadiologyEvent]
