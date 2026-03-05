from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class ReasonForPresentation(str, Enum):
    first_time = "first_time"
    unplanned_excision = "unplanned_excision"
    follow_up = "follow_up"


class StatusBeforeFollowUp(str, Enum):
    no_previous_therapy = "no_previous_therapy"
    locally_advanced_tumor = "locally_advanced_tumor"
    exophytic_growth = "exophytic_growth"


class StatusAfterFollowUp(str, Enum):
    partial_therapy_for_primary_tumor = "partial_therapy_for_primary_tumor"
    completed_therapy_for_primary_tumor = "completed_therapy_for_primary_tumor"
    other = "other"


class TreatmentBeforeFollowUp(str, Enum):
    none = "none"
    surgery = "surgery"
    radiotherapy = "radiotherapy"
    systemic_therapy = "systemic_therapy"
    surgery_radiotherapy = "surgery_radiotherapy"
    surgery_chemotherapy = "surgery_chemotherapy"
    radiotherapy_chemotherapy = "radiotherapy_chemotherapy"
    surgery_chemotherapy_radiotherapy = "surgery_chemotherapy_radiotherapy"


class FollowUpReason(str, Enum):
    in_context_of_primary_treatment = "in_context_of_primary_treatment"
    first_local_recurrence = "first_local_recurrence"
    in_context_of_treatment_for_first_local_recurrence = "in_context_of_treatment_for_first_local_recurrence"
    first_systemic_recurrence = "first_systemic_recurrence"
    in_context_of_first_systemic_recurrence = "in_context_of_first_systemic_recurrence"
    second_or_more_local_systemic_recurrences = "second_or_more_local_systemic_recurrences"
    important_follow_up_information_of_general_interest = "important_follow_up_information_of_general_interest"


class LastExecution(str, Enum):
    """
    Grund warum der Patient NICHT erneut am Sarkomaboard präsentiert wurde.
    WICHTIG: Nicht verwechseln mit der letzten Behandlung!
    """
    patient_related_factors = "patient_related_factors"
    physician_healthcare_provider_related_factors = "physician_healthcare_provider_related_factors"
    logistical_administrative_factors = "logistical_administrative_factors"
    no_re_presentation_at_sarcomaboard = "no_re_presentation_at_sarcomaboard"
    systemic_institutional_factors = "systemic_institutional_factors"
    disease_course = "disease_course"
    research_trial_related_factors = "research_trial_related_factors"
    no_categorization_possible = "no_categorization_possible"


class BoardDecision(str, Enum):
    """
    Board-Entscheidung für alle decision_* Felder.
    Constraint-Werte laut db/constraints/sarcoma_board/decision_surgery.yml
    """
    yes = "yes"
    yes_interventional_radiology = "yes_interventional_radiology"
    no = "no"
    undecided = "undecided"


class SarcomaBoardEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_sarcoma_boards Tabelle.
    Ein Sarkom-Board ist ein multidisziplinäres Tumor-Board zur Behandlungsplanung.
    """

    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")

    # Datum der Board-Präsentation (optional bei LLM-Extraktion)
    presentation_date: Optional[date] = Field(default=None, description="Datum der Board-Präsentation")

    # Grund und Status
    reason_for_presentation: Optional[str] = None
    status_before_follow_up: Optional[str] = None
    status_after_follow_up: Optional[str] = None
    status_after_follow_up_comment: Optional[str] = Field(default=None, max_length=1000)

    # Behandlungsverlauf
    treatment_before_follow_up: Optional[str] = None
    follow_up_reason: Optional[str] = None
    last_execution: Optional[str] = None
    unplanned_excision_date: Optional[date] = None

    # Fragestellung und Vorschlag
    question: Optional[str] = Field(default=None, max_length=2000, description="Fragestellung an das Board")
    proposed_procedure: Optional[str] = Field(default=None, max_length=2000, description="Vorgeschlagenes Vorgehen")

    # ECOG Performance Status (0-5)
    current_ecog: Optional[int] = Field(default=None, ge=0, le=5, description="ECOG Performance Status")

    # Board-Entscheidungen (DB-Feldnamen beachten!)
    decision_surgery: Optional[str] = None
    decision_surgery_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_radio_therapy: Optional[str] = None
    decision_radio_therapy_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_systemic_surgery: Optional[str] = None          # DB-Feldname: decision_systemic_surgery
    decision_systemic_surgery_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_follow_up: Optional[str] = None
    decision_follow_up_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_diagnostics: Optional[str] = None
    decision_diagnostics_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_palliative_care: Optional[str] = None
    decision_palliative_care_comment: Optional[str] = Field(default=None, max_length=1000)

    # Zusammenfassungen
    summary: Optional[str] = Field(default=None, max_length=5000, description="Zusammenfassung der Board-Sitzung")
    patient_history: Optional[str] = Field(default=None, max_length=2000)
    summary_patient_information: Optional[str] = Field(default=None, max_length=2000)
    summary_radiology: Optional[str] = Field(default=None, max_length=2000)
    summary_pathology: Optional[str] = Field(default=None, max_length=2000)
    further_details: Optional[str] = Field(default=None, max_length=2000)

    # Zusätzliche Informationen
    fast_track: bool = Field(default=False, description="Fast-Track Behandlung")
    whoops_surgery_institution_id: Optional[int] = Field(default=None, ge=0, description="Institution bei Whoops-Chirurgie")
    presenting_physician_id: Optional[int] = Field(default=None, ge=0, description="Präsentierender Arzt")

    @staticmethod
    def _normalize_reason_for_presentation(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/reason_for_presentation.yml:
        first_time, unplanned_excision, follow_up
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

        allowed = {"first_time", "unplanned_excision", "follow_up"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["unplanned excision", "whoops", "whoops-op", "whoops op", "unbeabsichtigte"]):
            return "unplanned_excision"
        if any(token in lower for token in ["first time", "erstvorstellung", "erstpräsentation", "primary diagnosis",
                                             "erstdiagnose", "neu vorgestellt", "first presentation"]):
            return "first_time"
        if any(token in lower for token in ["follow-up", "follow up", "verlauf", "kontrolle", "nachsorge",
                                             "second opinion", "recurrence", "metastasis", "treatment decision"]):
            return "follow_up"
        return raw

    @staticmethod
    def _normalize_status_before_follow_up(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/status_before_follow_up.yml:
        no_previous_therapy, locally_advanced_tumor, exophytic_growth
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

        allowed = {"no_previous_therapy", "locally_advanced_tumor", "exophytic_growth"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["exophytic", "exophytisch"]):
            return "exophytic_growth"
        if any(token in lower for token in ["locally advanced", "lokal fortgeschritten", "advanced tumor"]):
            return "locally_advanced_tumor"
        if any(token in lower for token in ["no previous", "keine vorbehandlung", "keine therapie", "pre-treatment",
                                             "pre treatment", "therapienaiv", "unbehandelt"]):
            return "no_previous_therapy"
        return raw

    @staticmethod
    def _normalize_status_after_follow_up(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/status_after_follow_up.yml:
        partial_therapy_for_primary_tumor, completed_therapy_for_primary_tumor, other
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

        allowed = {"partial_therapy_for_primary_tumor", "completed_therapy_for_primary_tumor", "other"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["completed therapy", "abgeschlossene therapie", "complete remission",
                                             "vollständige", "therapie abgeschlossen"]):
            return "completed_therapy_for_primary_tumor"
        if any(token in lower for token in ["partial therapy", "teilweise therapie", "partial remission",
                                             "partielle", "laufende therapie", "ongoing"]):
            return "partial_therapy_for_primary_tumor"
        if any(token in lower for token in ["other", "sonst", "ander", "stable disease", "progressive disease",
                                             "recurrence", "deceased"]):
            return "other"
        return raw

    @staticmethod
    def _normalize_treatment_before_follow_up(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/treatment_before_follow_up.yml:
        none, surgery, radiotherapy, systemic_therapy,
        surgery_radiotherapy, surgery_chemotherapy, radiotherapy_chemotherapy,
        surgery_chemotherapy_radiotherapy
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/+&]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {
            "none", "surgery", "radiotherapy", "systemic_therapy",
            "surgery_radiotherapy", "surgery_chemotherapy", "radiotherapy_chemotherapy",
            "surgery_chemotherapy_radiotherapy",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        has_surgery = any(token in lower for token in ["surgery", "chirurgie", "op ", "operation", "resektion", "resection"])
        has_radio = any(token in lower for token in ["radiotherapy", "radiotherapie", "strahlen", "bestrahlung"])
        has_chemo = any(token in lower for token in ["chemotherapy", "chemotherapie", "systemic therapy", "systemtherapie",
                                                      "systemic_therapy", "chemo"])

        if has_surgery and has_radio and has_chemo:
            return "surgery_chemotherapy_radiotherapy"
        if has_surgery and has_radio:
            return "surgery_radiotherapy"
        if has_surgery and has_chemo:
            return "surgery_chemotherapy"
        if has_radio and has_chemo:
            return "radiotherapy_chemotherapy"
        if has_surgery:
            return "surgery"
        if has_radio:
            return "radiotherapy"
        if has_chemo:
            return "systemic_therapy"
        if any(token in lower for token in ["none", "keine", "kein", "no treatment", "no prior"]):
            return "none"
        if any(token in lower for token in ["combined treatment", "kombiniert"]):
            return "surgery_chemotherapy_radiotherapy"
        return raw

    @staticmethod
    def _normalize_follow_up_reason(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/follow_up_reason.yml:
        in_context_of_primary_treatment, first_local_recurrence,
        in_context_of_treatment_for_first_local_recurrence,
        first_systemic_recurrence, in_context_of_first_systemic_recurrence,
        second_or_more_local_systemic_recurrences,
        important_follow_up_information_of_general_interest
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
            "in_context_of_primary_treatment", "first_local_recurrence",
            "in_context_of_treatment_for_first_local_recurrence",
            "first_systemic_recurrence", "in_context_of_first_systemic_recurrence",
            "second_or_more_local_systemic_recurrences",
            "important_follow_up_information_of_general_interest",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["second", "weitere", "multiple recurrence", "dritte", "dritter"]):
            return "second_or_more_local_systemic_recurrences"
        if any(token in lower for token in ["in context of treatment for first local", "behandlung erstes lokalrezidiv"]):
            return "in_context_of_treatment_for_first_local_recurrence"
        if any(token in lower for token in ["in context of first systemic", "behandlung erstes systemisches"]):
            return "in_context_of_first_systemic_recurrence"
        if any(token in lower for token in ["first local recurrence", "erstes lokalrezidiv", "first local"]):
            return "first_local_recurrence"
        if any(token in lower for token in ["first systemic recurrence", "erstes systemisches rezidiv", "first systemic"]):
            return "first_systemic_recurrence"
        if any(token in lower for token in ["important", "allgemein", "general interest"]):
            return "important_follow_up_information_of_general_interest"
        if any(token in lower for token in ["primary treatment", "erstbehandlung", "primary", "routine"]):
            return "in_context_of_primary_treatment"
        return raw

    @staticmethod
    def _normalize_last_execution(value) -> Optional[str]:
        """
        Normalisiert auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/last_execution.yml:
        patient_related_factors, physician_healthcare_provider_related_factors,
        logistical_administrative_factors, no_re_presentation_at_sarcomaboard,
        systemic_institutional_factors, disease_course,
        research_trial_related_factors, no_categorization_possible

        HINWEIS: Dieses Feld speichert den Grund für KEINE Wiedervorstellung am Board,
        NICHT die zuletzt durchgeführte Behandlung.
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
            "patient_related_factors", "physician_healthcare_provider_related_factors",
            "logistical_administrative_factors", "no_re_presentation_at_sarcomaboard",
            "systemic_institutional_factors", "disease_course",
            "research_trial_related_factors", "no_categorization_possible",
        }
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["patient related", "patientenseitig", "patient factor"]):
            return "patient_related_factors"
        if any(token in lower for token in ["physician", "arzt", "healthcare provider", "provider"]):
            return "physician_healthcare_provider_related_factors"
        if any(token in lower for token in ["logistical", "logistisch", "administrative", "administrativ"]):
            return "logistical_administrative_factors"
        if any(token in lower for token in ["no re-presentation", "keine wiedervorstellung", "no re presentation"]):
            return "no_re_presentation_at_sarcomaboard"
        if any(token in lower for token in ["systemic institutional", "institutionell", "systemisch"]):
            return "systemic_institutional_factors"
        if any(token in lower for token in ["disease course", "krankheitsverlauf", "krankheit"]):
            return "disease_course"
        if any(token in lower for token in ["research", "trial", "studie", "forschung"]):
            return "research_trial_related_factors"
        if any(token in lower for token in ["no categorization", "keine kategorisierung", "unclear", "other", "sonst"]):
            return "no_categorization_possible"
        # Old enum fallbacks: Surgery/Radiotherapy/etc. cannot meaningfully map → preserve raw
        return raw

    @staticmethod
    def _normalize_ecog(value) -> Optional[int]:
        """
        Normalisiert ECOG Performance Status auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/ecog.yml: 0, 1, 2, 3, 4, 5
        """
        if value is None:
            return None
        if isinstance(value, int):
            return value if 0 <= value <= 5 else None
        if isinstance(value, float):
            n = int(value)
            return n if 0 <= n <= 5 else None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None

        # Extract number from strings like "ECOG 2", "PS 1", "Performance Status 3", "2"
        numbers = re.findall(r"\d+", raw)
        if numbers:
            n = int(numbers[0])
            return n if 0 <= n <= 5 else None
        return None

    @staticmethod
    def _normalize_board_decision(value) -> Optional[str]:
        """
        Normalisiert Board-Entscheidungen auf gültige DB-Constraint-Werte.
        Constraint-Werte laut db/constraints/sarcoma_board/decision_surgery.yml:
        yes, yes_interventional_radiology, no, undecided
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        raw = value.strip()
        if not raw:
            return None
        lower = raw.lower()
        compact = re.sub(r"[\s\-/]+", "_", lower)
        compact = re.sub(r"[^a-z_]", "", compact)

        allowed = {"yes", "yes_interventional_radiology", "no", "undecided"}
        if lower in allowed:
            return lower
        if compact in allowed:
            return compact

        if any(token in lower for token in ["interventional radiology", "interventionelle radiologie", "ir"]):
            return "yes_interventional_radiology"
        if any(token in lower for token in ["yes", "ja", "empfohlen", "recommended", "indiziert", "indicated"]):
            return "yes"
        if any(token in lower for token in ["no", "nein", "nicht", "not indicated", "nicht indiziert", "abgelehnt"]):
            return "no"
        if any(token in lower for token in ["maybe", "unclear", "undecided", "unklar", "wird diskutiert",
                                             "offen", "not applicable", "nicht zutreffend", "fraglich"]):
            return "undecided"
        return raw

    @model_validator(mode="before")
    @classmethod
    def normalize_sarcoma_board_fields(cls, data):
        if not isinstance(data, dict):
            return data

        # Single-value constrained fields
        for field, normalizer in [
            ("reason_for_presentation", cls._normalize_reason_for_presentation),
            ("status_before_follow_up", cls._normalize_status_before_follow_up),
            ("status_after_follow_up", cls._normalize_status_after_follow_up),
            ("treatment_before_follow_up", cls._normalize_treatment_before_follow_up),
            ("follow_up_reason", cls._normalize_follow_up_reason),
            ("last_execution", cls._normalize_last_execution),
        ]:
            raw = data.get(field)
            normalized = normalizer(raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None
            else:
                data[field] = raw  # nicht mappbar aber Wert vorhanden → raw_text erhalten

        # current_ecog → constrained to 0-5
        ecog_raw = data.get("current_ecog")
        ecog_normalized = cls._normalize_ecog(ecog_raw)
        data["current_ecog"] = ecog_normalized

        # All decision_* fields share the same constraint
        decision_fields = [
            "decision_surgery",
            "decision_radio_therapy",
            "decision_systemic_surgery",
            "decision_follow_up",
            "decision_diagnostics",
            "decision_palliative_care",
        ]
        # Also handle legacy field name from old LLM output
        if "decision_systemic_therapy" in data and "decision_systemic_surgery" not in data:
            data["decision_systemic_surgery"] = data.pop("decision_systemic_therapy")
        if "decision_systemic_therapy_comment" in data and "decision_systemic_surgery_comment" not in data:
            data["decision_systemic_surgery_comment"] = data.pop("decision_systemic_therapy_comment")

        for field in decision_fields:
            raw = data.get(field)
            normalized = cls._normalize_board_decision(raw)
            if normalized is not None:
                data[field] = normalized
            elif raw is None or (isinstance(raw, str) and not raw.strip()):
                data[field] = None
            else:
                data[field] = raw  # nicht mappbar aber Wert vorhanden → raw_text erhalten

        return data

    @field_validator("presentation_date", "unplanned_excision_date", mode="before")
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
            s = s.split(' ')[0]
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        return None  # Unbekanntes Format → leer lassen statt Fehler


class SarcomaBoardEvents(BaseModel):
    """
    Wrapper für mehrere Sarkom-Board-Events, extrahiert aus einem Bericht.
    """
    events: List[SarcomaBoardEvent]
