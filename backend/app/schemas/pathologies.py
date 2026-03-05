from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List
import functools
import pathlib
import re

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


@functools.lru_cache(maxsize=None)
def _load_who_diagnosis_data() -> tuple:
    """
    Lädt einmalig (gecacht) alle erlaubten WHO-Diagnose-Codes und die Locale-Label-Map.

    Returns:
        allowed_codes  – frozenset aller Blatt-Codes aus who_diagnosis.yml
        label_to_code  – dict { lowercase_EN_label → code }
                         (aus croms.enums.en.yml, who_diagnosis-Sektion)
    """
    _root = pathlib.Path(__file__).resolve().parents[3]  # …/pdfrag/

    def _extract_leaves(node) -> list:
        if isinstance(node, str):
            return [node]
        if isinstance(node, dict):
            return _extract_leaves(node.get("children", []))
        if isinstance(node, list):
            result = []
            for item in node:
                result.extend(_extract_leaves(item))
            return result
        return []

    constraint_path = _root / "db/constraints/pathology/who_diagnosis.yml"
    with open(constraint_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    allowed_codes = frozenset(_extract_leaves(raw))

    locale_path = _root / "db/locales/croms.enums.en.yml"
    with open(locale_path, encoding="utf-8") as f:
        locale_raw = yaml.safe_load(f)

    who_labels: dict = (
        locale_raw.get("en", {})
                  .get("enums", {})
                  .get("croms", {})
                  .get("who_diagnosis", {})
    )
    label_to_code: dict = {}
    for code, label in who_labels.items():
        if isinstance(label, str) and not code.startswith("label_"):
            label_to_code[label.lower()] = code

    return allowed_codes, label_to_code


class BiopsyType(str, Enum):
    fine_needle = "fine_needle"
    core_biopsy = "core_biopsy"
    open_incisional_with_suspicion_of_sarcoma = "open_incisional_with_suspicion_of_sarcoma"
    open_incisional_without_suspicion_of_sarcoma = "open_incisional_without_suspicion_of_sarcoma"
    excisional_with_suspicion_of_sarcoma = "excisional_with_suspicion_of_sarcoma"
    excisional_without_supsicion_of_sarcoma_whoops = "excisional_without_supsicion_of_sarcoma_whoops"


class BiopsiedLesionType(str, Enum):
    biopsy_of_the_primary_tumor = "biopsy_of_the_primary_tumor"
    biopsy_of_local_recurrence = "biopsy_of_local_recurrence"
    biopsy_of_metastases = "biopsy_of_metastases"
    resection_of_the_primary_tumor = "resection_of_the_primary_tumor"
    resection_of_local_recurrence = "resection_of_local_recurrence"
    resection_of_metastases = "resection_of_metastases"


class PriorTreatment(str, Enum):
    no = "no"
    radiotherapy = "radiotherapy"
    chemotherapy = "chemotherapy"
    radiotherapy_and_chemotherapy = "radiotherapy_and_chemotherapy"
    unknown = "unknown"


class DiagnosticGrading(str, Enum):
    not_a_sarcoma = "not_a_sarcoma"
    g1 = "g1"
    g2 = "g2"
    g3 = "g3"
    benign = "benign"
    suspicious_of_malignancy = "suspicious_of_malignancy"
    non_diagnostic = "non_diagnostic"
    not_applicable = "not_applicable"
    intermediate = "intermediate"


class SurgicalMarginJudgment(str, Enum):
    ro_wide_margin = "ro_wide_margin"
    r1a_marginal_margin_planned_close_ultimative_positive = "r1a_marginal_margin_planned_close_ultimative_positive"
    r1b_marginal_margin_positive_after_tumor_bed_re_exicision = "r1b_marginal_margin_positive_after_tumor_bed_re_exicision"
    r1c_marginal_margin_inadvertent_positive_margin = "r1c_marginal_margin_inadvertent_positive_margin"
    r2_intralesional_margin = "r2_intralesional_margin"
    curettage = "curettage"
    not_applicable_because_no_sarcoma = "not_applicable_because_no_sarcoma"


class BiologicalBarrier(str, Enum):
    none = "none"
    fascia = "fascia"
    adventitia = "adventitia"
    perineurium = "perineurium"
    periosteum = "periosteum"
    growth_plate = "growth_plate"
    other = "other"
    non_applicable = "non_applicable"


class TestPerformedStatus(str, Enum):
    yes = "yes"
    no = "no"
    not_yet_but_planned = "not_yet_but_planned"


class ReportResult(str, Enum):
    positive = "positive"
    negative = "negative"
    not_interpretable = "not_interpretable"
    in_progress = "in_progress"


class EORTCResponseGrade(str, Enum):
    """
    EORTC Response Grade für Sarkom-Response nach neoadjuvanter Therapie.
    """
    grade_a = "grade_a"
    grade_b = "grade_b"
    grade_c = "grade_c"
    grade_d = "grade_d"
    grade_e = "grade_e"


class MitosesPerHPF(str, Enum):
    less_than_10 = "less_than_10_mitoses_per_10hpf"
    ten_to_19 = "10_to_19_mitoses_per_10hpf"
    more_than_19 = "more_than_19_mitoses_per_10hpf"
    not_applicable = "not_applicable_in_cases_with_neoadjuvant_therapy_necrosis"


class ExtentOfNecrosis(str, Enum):
    less_than_10_percent = "less_than_10_percent"
    eleven_to_20_percent = "11_to_20_percent"
    twentyone_to_30_percent = "21_to_30_percent"
    thirtyone_to_40_percent = "31_to_40_percent"
    fortyone_to_50_percent = "41_to_50_percent"
    fiftyone_to_60_percent = "51_to_60_percent"
    sixtyone_to_70_percent = "61_to_70_percent"
    seventyone_to_80_percent = "71_to_80_percent"
    eightyone_to_90_percent = "81_to_90_percent"
    more_than_90_percent = "more_than_90_percent"


class ProliferationIndex(str, Enum):
    less_than_10_percent = "less_than_10_percent"
    eleven_to_20_percent = "11_to_20_percent"
    twentyone_to_30_percent = "21_to_30_percent"
    thirtyone_to_40_percent = "31_to_40_percent"
    fortyone_to_50_percent = "41_to_50_percent"
    fiftyone_to_60_percent = "51_to_60_percent"
    sixtyone_to_70_percent = "61_to_70_percent"
    seventyone_to_80_percent = "71_to_80_percent"
    eightyone_to_90_percent = "81_to_90_percent"
    more_than_90_percent = "more_than_90_percent"
    not_applicable_because_of_therapy = "not_applicable_because_of_therapy_before_biopsy_or_necrosis"


class PathologyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_pathologies Tabelle.
    Pathologie-Befund nach Biopsie oder Resektion.
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_pathologist_id: Optional[int] = Field(default=None, ge=0, description="Verantwortlicher Pathologe")

    # Biopsie/Resektions-Details
    biopsy_type: Optional[str] = None
    biopsied_lesion_type: Optional[str] = None
    biopsy_resection_date: Optional[date] = None

    # Befund-Daten
    registrate_date: Optional[date] = Field(default=None, description="Registrierungsdatum")
    first_report_date: Optional[date] = Field(default=None, description="Datum Erstbefund")
    final_report_date: Optional[date] = Field(default=None, description="Datum Endbefund")
    report_date: Optional[date] = Field(default=None, description="Befunddatum (allgemein)")

    # Vorbehandlung
    prior_treatment: Optional[str] = None

    # Diagnose nach WHO-Klassifikation
    who_diagnosis: Optional[str] = Field(
        default=None,
        max_length=500,
        description="WHO-Diagnose (z.B. 'High-grade myxofibrosarcoma')"
    )

    # Grading
    diagnostic_grading: Optional[str] = None

    # Chirurgischer Rand
    judgment_of_surgical_margin: Optional[str] = None
    closest_distance_to_margin_mm: Optional[int] = Field(
        default=None,
        ge=0,
        description="Abstand zum nächsten Resektionsrand in mm"
    )
    biological_barrier_to_closest_margin: Optional[BiologicalBarrier] = None
    biological_barrier_to_closest_margin_comment: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    # Tumor-Charakteristika
    proliferation_index: Optional[str] = Field(
        default=None,
        max_length=200,
        description="z.B. 'Ki-67: 40%' → mapped to constrained range value"
    )
    mitoses_per_10hpf: Optional[str] = Field(
        default=None,
        description="Mitosen pro 10 High-Power-Fields"
    )
    extent_of_necrosis: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Nekroseanteil (z.B. '<10%' oder '50-90%')"
    )

    # Response nach neoadjuvanter Therapie
    eortc_response_grade: Optional[str] = None

    # Molekularpathologie
    ihc_performed_status: Optional[str] = Field(
        default=None,
        description="Immunhistochemie durchgeführt?"
    )
    ihc_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="IHC-Ergebnis"
    )

    fish_performed_status: Optional[str] = Field(
        default=None,
        description="FISH durchgeführt?"
    )
    fish_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="FISH-Ergebnis (z.B. MDM2-Amplifikation)"
    )

    rna_performed_status: Optional[str] = Field(
        default=None,
        description="RNA-Sequenzierung durchgeführt?"
    )
    rna_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="RNA-Sequenzierungs-Ergebnis (z.B. Fusionsgene)"
    )

    dna_performed_status: Optional[str] = Field(
        default=None,
        description="DNA-Sequenzierung durchgeführt?"
    )
    dna_result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="DNA-Sequenzierungs-Ergebnis (z.B. Mutationen)"
    )

    # Vollständiger Befundtext
    report: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Vollständiger Pathologie-Befund"
    )

    @staticmethod
    def _normalize_who_diagnosis(value) -> Optional[str]:
        """
        Normalisiert den WHO-Diagnosebegriff auf einen gültigen DB-Code.
        Constraint-Werte laut db/constraints/pathology/who_diagnosis.yml (~200 Leaf-Codes).
        Labels aus db/locales/croms.enums.en.yml (who_diagnosis-Sektion).

        Priorität:
          1. Bereits ein gültiger Code        → Code zurückgeben
          2. Compact-Form eines Codes         → Code zurückgeben
          3. Exakter Label-Text (EN)          → Code zurückgeben  (z.B. "Myxoid liposarcoma")
          4. Partieller Label-Match (eindeutig) → Code zurückgeben
          5. Kein Mapping                     → raw_text erhalten
          6. Kein Wert (None/leer)            → None
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None

        raw = value.strip()
        if not raw:
            return None

        try:
            allowed_codes, label_to_code = _load_who_diagnosis_data()
        except Exception:
            return raw  # Datei nicht ladbar → raw_text erhalten

        lower = raw.lower()
        compact = re.sub(r"[\s\-/\.]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        # 1. Exakter Code-Match
        if lower in allowed_codes:
            return lower
        # 2. Compact-Form
        if compact in allowed_codes:
            return compact

        # 3. Exakter Label-Match (EN)
        if lower in label_to_code:
            return label_to_code[lower]

        # 4. Partieller Label-Match – nur wenn eindeutig (genau 1 Treffer)
        hits = [code for lbl, code in label_to_code.items() if lower in lbl or lbl in lower]
        if len(hits) == 1:
            return hits[0]

        # 5. Kein Mapping → raw_text erhalten
        return raw

    @staticmethod
    def _normalize_biological_barrier(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/biological_barrier_to_closest_margin.yml:
        none, fascia, adventitia, perineurium, periosteum, growth_plate, other, non_applicable
        """
        if value is None:
            return "none"

        if isinstance(value, BiologicalBarrier):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return "none"

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {b.value for b in BiologicalBarrier}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Synonym-Mapping (DE/EN)
        if any(token in lower for token in ["n/a", "na", "not applicable", "nicht zutreffend", "nicht anwendbar"]):
            return "non_applicable"
        if any(token in lower for token in ["none", "keine", "kein", "ohne"]):
            return "none"
        if any(token in lower for token in ["fascia", "faszie"]):
            return "fascia"
        if "adventitia" in lower:
            return "adventitia"
        if any(token in lower for token in ["perineurium", "perineural", "perineuralschicht"]):
            return "perineurium"
        if any(token in lower for token in ["periosteum", "periost"]):
            return "periosteum"
        if any(token in lower for token in ["growth plate", "growth_plate", "wachstumsfuge", "epiphysenfuge"]):
            return "growth_plate"
        if any(token in lower for token in ["other", "sonst", "ander"]):
            return "other"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_biopsied_lesion_type(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/biopsied_lesion_type.yml:
        biopsy_of_the_primary_tumor, biopsy_of_local_recurrence, biopsy_of_metastases,
        resection_of_the_primary_tumor, resection_of_local_recurrence, resection_of_metastases
        """
        if value is None:
            return None

        if isinstance(value, BiopsiedLesionType):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in BiopsiedLesionType}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Legacy/EN mappings from previous enum representation
        if "primary" in lower and "biopsy" in lower:
            return "biopsy_of_the_primary_tumor"
        if any(token in lower for token in ["recurrent", "recurrence", "lokalrezidiv", "local recurrence"]) and "biopsy" in lower:
            return "biopsy_of_local_recurrence"
        if any(token in lower for token in ["metastasis", "metastases", "metastase"]) and "biopsy" in lower:
            return "biopsy_of_metastases"
        if "primary" in lower and any(token in lower for token in ["resection", "resect", "resektion"]):
            return "resection_of_the_primary_tumor"
        if any(token in lower for token in ["recurrent", "recurrence", "lokalrezidiv", "local recurrence"]) and any(token in lower for token in ["resection", "resect", "resektion"]):
            return "resection_of_local_recurrence"
        if any(token in lower for token in ["metastasis", "metastases", "metastase"]) and any(token in lower for token in ["resection", "resect", "resektion"]):
            return "resection_of_metastases"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_biopsy_type(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/biopsy_type.yml:
        fine_needle, core_biopsy, open_incisional_with_suspicion_of_sarcoma,
        open_incisional_without_suspicion_of_sarcoma, excisional_with_suspicion_of_sarcoma,
        excisional_without_supsicion_of_sarcoma_whoops
        """
        if value is None:
            return None

        if isinstance(value, BiopsyType):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in BiopsyType}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["fine needle", "fna", "feinnadel"]):
            return "fine_needle"
        if any(token in lower for token in ["core biopsy", "core-needle", "stanzbiops", "tru-cut", "trucut"]):
            return "core_biopsy"
        if "incisional" in lower or "inzisional" in lower:
            if any(token in lower for token in ["without suspicion", "ohne verdacht", "kein verdacht"]):
                return "open_incisional_without_suspicion_of_sarcoma"
            return "open_incisional_with_suspicion_of_sarcoma"
        if "excisional" in lower or "exzisional" in lower:
            if any(token in lower for token in ["without suspicion", "ohne verdacht", "kein verdacht", "whoops"]):
                return "excisional_without_supsicion_of_sarcoma_whoops"
            return "excisional_with_suspicion_of_sarcoma"

        # Kein Mapping → raw_text erhalten (nicht null setzen)
        return raw

    @staticmethod
    def _normalize_eortc_response_grade(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/eortc_response_grade.yml:
        grade_a, grade_b, grade_c, grade_d, grade_e
        """
        if value is None:
            return None

        if isinstance(value, EORTCResponseGrade):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in EORTCResponseGrade}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Legacy mappings from previous representation
        if any(token in lower for token in ["grade 1", "grade i", "no therapy effect"]):
            return "grade_a"
        if any(token in lower for token in ["grade 2", "grade ii", "< 50% necrosis", "unter 50", "less than 50"]):
            return "grade_b"
        if any(token in lower for token in ["grade 3", "grade iii", "50-90", "50 to 90"]):
            return "grade_c"
        if any(token in lower for token in ["grade 4", "grade iv", "> 90% necrosis", "über 90", "more than 90"]):
            return "grade_d"
        if any(token in lower for token in ["grade 5", "grade v", "no viable", "complete response"]):
            return "grade_e"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_extent_of_necrosis(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/extent_of_necrosis.yml:
        less_than_10_percent, 11_to_20_percent, 21_to_30_percent, 31_to_40_percent, 41_to_50_percent,
        51_to_60_percent, 61_to_70_percent, 71_to_80_percent, 81_to_90_percent, more_than_90_percent
        """
        if value is None:
            return None

        if isinstance(value, ExtentOfNecrosis):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower().replace(",", ".")
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {v.value for v in ExtentOfNecrosis}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["<10", "unter 10", "less than 10"]):
            return "less_than_10_percent"
        if any(token in lower for token in ["11-20", "11 to 20", "11_20"]):
            return "11_to_20_percent"
        if any(token in lower for token in ["21-30", "21 to 30", "21_30"]):
            return "21_to_30_percent"
        if any(token in lower for token in ["31-40", "31 to 40", "31_40"]):
            return "31_to_40_percent"
        if any(token in lower for token in ["41-50", "41 to 50", "41_50"]):
            return "41_to_50_percent"
        if any(token in lower for token in ["51-60", "51 to 60", "51_60"]):
            return "51_to_60_percent"
        if any(token in lower for token in ["61-70", "61 to 70", "61_70"]):
            return "61_to_70_percent"
        if any(token in lower for token in ["71-80", "71 to 80", "71_80"]):
            return "71_to_80_percent"
        if any(token in lower for token in ["81-90", "81 to 90", "81_90"]):
            return "81_to_90_percent"
        if any(token in lower for token in [">90", "über 90", "more than 90"]):
            return "more_than_90_percent"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_prior_treatment(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/prior_treatment.yml:
        no, radiotherapy, chemotherapy, radiotherapy_and_chemotherapy, unknown
        """
        if value is None:
            return "unknown"

        if isinstance(value, PriorTreatment):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return "unknown"

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in PriorTreatment}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Legacy mappings
        has_radio = any(token in lower for token in ["radiotherapy", "radio therapy", "radiatio", "bestrahl", "strahlen"])
        has_chemo = any(token in lower for token in ["chemotherapy", "chemo", "chemotherapie"])
        has_combined = any(token in lower for token in ["combined", "kombiniert", "kombination", "combined treatment"])

        if (has_radio and has_chemo) or has_combined:
            return "radiotherapy_and_chemotherapy"
        if has_radio:
            return "radiotherapy"
        if has_chemo:
            return "chemotherapy"
        if any(token in lower for token in ["none", "no", "kein", "keine", "ohne", "no prior treatment"]):
            return "no"
        if any(token in lower for token in ["unknown", "unklar", "unbekannt", "n/a", "na"]):
            return "unknown"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_judgment_of_surgical_margin(value) -> Optional[str]:
        """
        Normalisiert den chirurgischen Resektionsrand auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/judgment_of_surgical_margin.yml:
        ro_wide_margin, r1a_marginal_margin_planned_close_ultimative_positive,
        r1b_marginal_margin_positive_after_tumor_bed_re_exicision,
        r1c_marginal_margin_inadvertent_positive_margin, r2_intralesional_margin,
        curettage, not_applicable_because_no_sarcoma
        """
        if value is None:
            return None

        if isinstance(value, SurgicalMarginJudgment):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {v.value for v in SurgicalMarginJudgment}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Legacy mappings from previous representation / free text
        if any(token in lower for token in ["r0", "ro", "wide margin", "in sano", "negative margins"]):
            return "ro_wide_margin"
        if any(token in lower for token in ["r1a", "planned close", "ultimative positive"]):
            return "r1a_marginal_margin_planned_close_ultimative_positive"
        if any(token in lower for token in ["r1b", "tumor bed", "re-excision", "re exicision", "re-exicision"]):
            return "r1b_marginal_margin_positive_after_tumor_bed_re_exicision"
        if any(token in lower for token in ["r1c", "inadvertent positive", "accidental positive"]):
            return "r1c_marginal_margin_inadvertent_positive_margin"
        # "R1" ohne Subtyp ist fachlich mehrdeutig (R1a/R1b/R1c) -> nicht raten
        # und stattdessen raw_text erhalten.
        if any(token in lower for token in ["r2", "intralesional", "macroscopic residual", "makroskopisch positiv"]):
            return "r2_intralesional_margin"
        if any(token in lower for token in ["curettage", "kürettage", "kurettage"]):
            return "curettage"
        if any(token in lower for token in ["not applicable", "no sarcoma", "kein sarkom", "nicht zutreffend"]):
            return "not_applicable_because_no_sarcoma"

        # No mapping hit: preserve raw text for UI/CSV instead of dropping value
        return raw

    @staticmethod
    def _normalize_diagnostic_grading(value) -> Optional[str]:
        """
        Normalisiert Synonyme auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/diagnostic_grading.yml:
        not_a_sarcoma, g1, g2, g3, benign, suspicious_of_malignancy,
        non_diagnostic, not_applicable, intermediate

        Logik:
        - Kein Wert (None/leer) → None (Feld bleibt leer)
        - Wert mappbar → gemappter Constraint-Wert (Priorität)
        - Wert nicht mappbar → raw_text erhalten (nicht null)
        """
        if value is None:
            return None

        if isinstance(value, DiagnosticGrading):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-\(\)]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in DiagnosticGrading}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # G-Grading und alte Enum-Schreibweisen (DE/EN)
        if any(token in lower for token in ["g1", "grade 1", "grade i", "well differentiated", "gut differenziert", "niedriggradig", "low grade"]):
            return "g1"
        if any(token in lower for token in ["g2", "grade 2", "grade ii", "moderately differentiated", "mäßig differenziert", "mittelgradig"]):
            return "g2"
        if any(token in lower for token in ["g3", "grade 3", "grade iii", "poorly differentiated", "schlecht differenziert", "hochgradig", "high grade"]):
            return "g3"
        if any(token in lower for token in ["gx", "cannot be assessed", "nicht beurteilbar"]):
            return "not_applicable"
        if any(token in lower for token in ["not a sarcoma", "kein sarkom", "no sarcoma", "non-sarcoma", "non sarcoma"]):
            return "not_a_sarcoma"
        if any(token in lower for token in ["benign", "gutartig", "benigne"]):
            return "benign"
        if any(token in lower for token in ["suspicious", "verdächtig", "suspekt", "verdacht auf"]):
            return "suspicious_of_malignancy"
        if any(token in lower for token in ["non diagnostic", "non-diagnostic", "nicht diagnostisch", "nicht verwertbar", "inadequate", "unzureichend", "nicht auswertbar"]):
            return "non_diagnostic"
        if any(token in lower for token in ["n/a", "not applicable", "nicht zutreffend", "nicht anwendbar"]):
            return "not_applicable"
        if any(token in lower for token in ["intermediate", "intermediär", "intermediary"]):
            return "intermediate"

        # Kein Mapping → raw_text erhalten (nicht null setzen)
        return raw

    @staticmethod
    def _normalize_mitoses_per_10hpf(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/mitoses_per_10hpf.yml:
        less_than_10_mitoses_per_10hpf, 10_to_19_mitoses_per_10hpf,
        more_than_19_mitoses_per_10hpf,
        not_applicable_in_cases_with_neoadjuvant_therapy_necrosis

        Logik:
        - Kein Wert → None (Feld leer)
        - Mappbar → Constraint-Wert (Priorität)
        - Nicht mappbar → raw_text erhalten
        """
        if value is None:
            return None

        if isinstance(value, MitosesPerHPF):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {v.value for v in MitosesPerHPF}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # n/a → not_applicable
        if any(token in lower for token in ["n/a", "not applicable", "nicht zutreffend", "neoadjuvant", "nicht anwendbar", "necrosis"]):
            return "not_applicable_in_cases_with_neoadjuvant_therapy_necrosis"

        # Versuche Zahl aus dem Text zu extrahieren (z.B. "15/10 HPF", "5 Mitosen", "25")
        numbers = re.findall(r"\d+", raw)
        if numbers:
            n = int(numbers[0])
            if n < 10:
                return "less_than_10_mitoses_per_10hpf"
            elif n <= 19:
                return "10_to_19_mitoses_per_10hpf"
            else:
                return "more_than_19_mitoses_per_10hpf"

        # Textuelles Mapping (DE/EN)
        if any(token in lower for token in ["<10", "< 10", "less than 10", "weniger als 10", "unter 10"]):
            return "less_than_10_mitoses_per_10hpf"
        if any(token in lower for token in ["10-19", "10 to 19", "10 bis 19"]):
            return "10_to_19_mitoses_per_10hpf"
        if any(token in lower for token in [">19", "> 19", "more than 19", "mehr als 19", "über 19"]):
            return "more_than_19_mitoses_per_10hpf"

        # Kein Mapping → raw_text erhalten
        return raw

    @staticmethod
    def _normalize_report_result(value) -> Optional[str]:
        """
        Normalisiert Ergebnis-Felder (IHC, FISH, RNA, DNA) auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/report_result.yml:
        positive, negative, not_interpretable, in_progress

        Logik:
        - Kein Wert (None/leer) → None (Feld bleibt leer)
        - Wert mappbar → gemappter Constraint-Wert (Priorität)
        - Wert nicht mappbar → raw_text erhalten (nicht null)
        """
        if value is None:
            return None

        if isinstance(value, ReportResult):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in ReportResult}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Synonym-Mapping (DE/EN)
        if any(token in lower for token in ["positiv", "positive", "pos.", "detected", "nachgewiesen", "amplifiziert", "amplified", "mutiert", "mutated"]):
            return "positive"
        if any(token in lower for token in ["negativ", "negative", "neg.", "not detected", "nicht nachgewiesen", "nicht amplifiziert", "not amplified", "wildtyp", "wild type", "wild-type"]):
            return "negative"
        if any(token in lower for token in ["nicht interpretierbar", "not interpretable", "uninterpretable", "nicht auswertbar", "nicht verwertbar", "nicht beurteilbar", "inadequate", "n/a"]):
            return "not_interpretable"
        if any(token in lower for token in ["in progress", "in bearbeitung", "ausstehend", "pending", "in arbeit", "wird durchgeführt"]):
            return "in_progress"

        # Kein Mapping → raw_text erhalten (nicht null setzen)
        return raw

    @staticmethod
    def _normalize_report_status(value) -> Optional[str]:
        """
        Normalisiert Status-Felder (IHC/FISH/RNA/DNA performed_status) auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/report_status.yml:
        yes, no, not_yet_but_planned

        Logik:
        - Kein Wert (None/leer) → None (Feld bleibt leer)
        - Wert mappbar → gemappter Constraint-Wert (Priorität)
        - Wert nicht mappbar → raw_text erhalten (nicht null)
        """
        if value is None:
            return None

        if isinstance(value, TestPerformedStatus):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower()
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {v.value for v in TestPerformedStatus}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # Synonym-Mapping (DE/EN)
        if any(token in lower for token in ["yes", "performed", "durchgeführt", "gemacht", "done", "vorhanden", "available"]):
            return "yes"
        if any(token in lower for token in ["no", "not performed", "nicht durchgeführt", "nicht gemacht", "none", "keine", "kein", "not applicable", "n/a"]):
            return "no"
        if any(token in lower for token in ["planned", "not yet", "ausstehend", "pending", "geplant", "in planung", "wird geplant"]):
            return "not_yet_but_planned"

        # Kein Mapping → raw_text erhalten (nicht null setzen)
        return raw

    @staticmethod
    def _normalize_proliferation_index(value) -> Optional[str]:
        """
        Normalisiert Ki-67/Proliferationsindex auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/pathology/proliferation_index.yml:
        less_than_10_percent, 11_to_20_percent, 21_to_30_percent, 31_to_40_percent,
        41_to_50_percent, 51_to_60_percent, 61_to_70_percent, 71_to_80_percent,
        81_to_90_percent, more_than_90_percent,
        not_applicable_because_of_therapy_before_biopsy_or_necrosis

        Logik:
        - Kein Wert (None/leer) → None (Feld bleibt leer)
        - Wert mappbar → gemappter Constraint-Wert (Priorität)
        - Wert nicht mappbar → raw_text erhalten (nicht null)
        """
        if value is None:
            return None

        if isinstance(value, ProliferationIndex):
            return value.value

        if not isinstance(value, str):
            return None

        raw = value.strip()
        if raw == "":
            return None

        lower = raw.lower().replace(",", ".")
        compact = re.sub(r"[\s\-]+", "_", lower)
        compact = re.sub(r"[^a-z0-9_]", "", compact)

        allowed = {v.value for v in ProliferationIndex}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        # n/a → not_applicable
        if any(token in lower for token in ["n/a", "not applicable", "neoadjuvant", "necrosis", "nicht anwendbar", "nicht zutreffend"]):
            return "not_applicable_because_of_therapy_before_biopsy_or_necrosis"

        # Extrahiere Prozentzahl aus Text (z.B. "Ki-67: 40%", "MIB1: 25%", "Ki67 35%")
        # Suche zuerst explizit nach Prozentangabe (Zahl gefolgt von %)
        percent_match = re.search(r"(\d+(?:[.,]\d+)?)\s*%", raw)
        if percent_match:
            n = float(percent_match.group(1).replace(",", "."))
            if n < 11:
                return "less_than_10_percent"
            elif n < 21:
                return "11_to_20_percent"
            elif n < 31:
                return "21_to_30_percent"
            elif n < 41:
                return "31_to_40_percent"
            elif n < 51:
                return "41_to_50_percent"
            elif n < 61:
                return "51_to_60_percent"
            elif n < 71:
                return "61_to_70_percent"
            elif n < 81:
                return "71_to_80_percent"
            elif n <= 90:
                return "81_to_90_percent"
            else:
                return "more_than_90_percent"

        # Textuelles Mapping (DE/EN)
        if any(token in lower for token in ["<10", "< 10", "less than 10", "weniger als 10", "unter 10"]):
            return "less_than_10_percent"
        if any(token in lower for token in ["11-20", "11 to 20", "11 bis 20"]):
            return "11_to_20_percent"
        if any(token in lower for token in ["21-30", "21 to 30", "21 bis 30"]):
            return "21_to_30_percent"
        if any(token in lower for token in ["31-40", "31 to 40", "31 bis 40"]):
            return "31_to_40_percent"
        if any(token in lower for token in ["41-50", "41 to 50", "41 bis 50"]):
            return "41_to_50_percent"
        if any(token in lower for token in ["51-60", "51 to 60", "51 bis 60"]):
            return "51_to_60_percent"
        if any(token in lower for token in ["61-70", "61 to 70", "61 bis 70"]):
            return "61_to_70_percent"
        if any(token in lower for token in ["71-80", "71 to 80", "71 bis 80"]):
            return "71_to_80_percent"
        if any(token in lower for token in ["81-90", "81 to 90", "81 bis 90"]):
            return "81_to_90_percent"
        if any(token in lower for token in [">90", "> 90", "über 90", "more than 90"]):
            return "more_than_90_percent"

        # Kein Mapping → raw_text erhalten (nicht null setzen)
        return raw

    @model_validator(mode="before")
    @classmethod
    def normalize_pathology_fields(cls, data):
        if not isinstance(data, dict):
            return data

        # biopsy_type to DB-constrained values
        biopsy_field = "biopsy_type"
        biopsy_raw = data.get(biopsy_field)
        biopsy_normalized = cls._normalize_biopsy_type(biopsy_raw)
        if biopsy_normalized is not None:
            data[biopsy_field] = biopsy_normalized

        # biopsied_lesion_type to DB-constrained values
        lesion_field = "biopsied_lesion_type"
        lesion_raw = data.get(lesion_field)
        lesion_normalized = cls._normalize_biopsied_lesion_type(lesion_raw)
        if lesion_normalized is not None:
            data[lesion_field] = lesion_normalized

        # who_diagnosis to DB-constrained code values
        who_field = "who_diagnosis"
        who_raw = data.get(who_field)
        who_normalized = cls._normalize_who_diagnosis(who_raw)
        if who_normalized is not None:
            data[who_field] = who_normalized
        elif who_raw is None or (isinstance(who_raw, str) and not who_raw.strip()):
            data[who_field] = None

        # eortc_response_grade to DB-constrained values
        eortc_field = "eortc_response_grade"
        eortc_raw = data.get(eortc_field)
        eortc_normalized = cls._normalize_eortc_response_grade(eortc_raw)
        if eortc_normalized is not None:
            data[eortc_field] = eortc_normalized

        # prior_treatment to DB-constrained values
        prior_field = "prior_treatment"
        prior_raw = data.get(prior_field)
        prior_normalized = cls._normalize_prior_treatment(prior_raw)
        if prior_normalized is not None:
            data[prior_field] = prior_normalized

        # judgment_of_surgical_margin to DB-constrained values
        margin_field = "judgment_of_surgical_margin"
        margin_raw = data.get(margin_field)
        margin_normalized = cls._normalize_judgment_of_surgical_margin(margin_raw)
        if margin_normalized is not None:
            data[margin_field] = margin_normalized

        # extent_of_necrosis to DB-constrained values
        necrosis_field = "extent_of_necrosis"
        necrosis_raw = data.get(necrosis_field)
        necrosis_normalized = cls._normalize_extent_of_necrosis(necrosis_raw)
        if necrosis_normalized is not None:
            data[necrosis_field] = necrosis_normalized

        # diagnostic_grading to DB-constrained values
        grading_field = "diagnostic_grading"
        grading_raw = data.get(grading_field)
        grading_normalized = cls._normalize_diagnostic_grading(grading_raw)
        if grading_normalized is not None:
            data[grading_field] = grading_normalized
        elif grading_raw is None or (isinstance(grading_raw, str) and not grading_raw.strip()):
            data[grading_field] = None  # Kein Wert → leer lassen

        # proliferation_index to DB-constrained values
        prolif_field = "proliferation_index"
        prolif_raw = data.get(prolif_field)
        prolif_normalized = cls._normalize_proliferation_index(prolif_raw)
        if prolif_normalized is not None:
            data[prolif_field] = prolif_normalized
        elif prolif_raw is None or (isinstance(prolif_raw, str) and not prolif_raw.strip()):
            data[prolif_field] = None  # Kein Wert → leer lassen

        # mitoses_per_10hpf to DB-constrained values
        mitoses_field = "mitoses_per_10hpf"
        mitoses_raw = data.get(mitoses_field)
        mitoses_normalized = cls._normalize_mitoses_per_10hpf(mitoses_raw)
        if mitoses_normalized is not None:
            data[mitoses_field] = mitoses_normalized

        # ihc_result / fish_result / rna_result / dna_result to DB-constrained values
        for result_field in ("ihc_result", "fish_result", "rna_result", "dna_result"):
            result_raw = data.get(result_field)
            result_normalized = cls._normalize_report_result(result_raw)
            if result_normalized is not None:
                data[result_field] = result_normalized
            elif result_raw is None or (isinstance(result_raw, str) and not result_raw.strip()):
                data[result_field] = None  # Kein Wert → leer lassen

        # ihc/fish/rna/dna performed_status to DB-constrained values
        for status_field in ("ihc_performed_status", "fish_performed_status", "rna_performed_status", "dna_performed_status"):
            status_raw = data.get(status_field)
            status_normalized = cls._normalize_report_status(status_raw)
            if status_normalized is not None:
                data[status_field] = status_normalized
            elif status_raw is None or (isinstance(status_raw, str) and not status_raw.strip()):
                data[status_field] = None  # Kein Wert → leer lassen

        field_name = "biological_barrier_to_closest_margin"
        comment_field = "biological_barrier_to_closest_margin_comment"
        raw_value = data.get(field_name)
        normalized = cls._normalize_biological_barrier(raw_value)

        # Wenn kein verwertbarer Wert vorliegt, immer "none" setzen
        if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
            data[field_name] = "none"
            return data

        # Gültig/synonym gemappt
        if normalized is not None:
            data[field_name] = normalized
            return data

        # Nicht mappbar: Originalwert in raw_text sichern, Feld selbst leer lassen
        raw_text = str(raw_value).strip()
        existing_comment = data.get(comment_field)
        raw_note = f"raw_text: {raw_text}"
        if existing_comment and raw_note not in existing_comment:
            data[comment_field] = f"{existing_comment}\n{raw_note}"
        elif not existing_comment:
            data[comment_field] = raw_note

        data[field_name] = None
        return data

    @field_validator(
        "biopsy_resection_date",
        "registrate_date",
        "first_report_date",
        "final_report_date",
        "report_date",
        mode="before"
    )
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


class PathologyEvents(BaseModel):
    """
    Wrapper für mehrere Pathologie-Events, extrahiert aus einem Bericht.
    """
    events: List[PathologyEvent]
