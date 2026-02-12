from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class ReasonForPresentation(str, Enum):
    primary_diagnosis = "Primary diagnosis"
    follow_up = "Follow-up"
    second_opinion = "Second opinion"
    recurrence = "Recurrence"
    metastasis = "Metastasis"
    treatment_decision = "Treatment decision"
    complication = "Complication"
    other = "Other"


class StatusBeforeFollowUp(str, Enum):
    pre_treatment = "Pre-treatment"
    during_treatment = "During treatment"
    post_treatment = "Post-treatment"
    recurrence = "Recurrence"
    stable_disease = "Stable disease"
    progressive_disease = "Progressive disease"
    other = "Other"


class StatusAfterFollowUp(str, Enum):
    complete_remission = "Complete remission"
    partial_remission = "Partial remission"
    stable_disease = "Stable disease"
    progressive_disease = "Progressive disease"
    recurrence = "Recurrence"
    deceased = "Deceased"
    other = "Other"


class TreatmentBeforeFollowUp(str, Enum):
    none = "None"
    surgery = "Surgery"
    radiotherapy = "Radiotherapy"
    chemotherapy = "Chemotherapy"
    combined_treatment = "Combined treatment"
    other = "Other"


class FollowUpReason(str, Enum):
    routine_surveillance = "Routine surveillance"
    symptom_evaluation = "Symptom evaluation"
    treatment_response_assessment = "Treatment response assessment"
    pre_treatment_evaluation = "Pre-treatment evaluation"
    post_treatment_evaluation = "Post-treatment evaluation"
    other = "Other"


class LastExecution(str, Enum):
    surgery = "Surgery"
    radiotherapy = "Radiotherapy"
    chemotherapy = "Chemotherapy"
    systemic_therapy = "Systemic therapy"
    biopsy = "Biopsy"
    imaging = "Imaging"
    none = "None"
    other = "Other"


class BoardDecision(str, Enum):
    yes = "Yes"
    no = "No"
    maybe = "Maybe/Unclear"
    not_applicable = "Not applicable"


class SarcomaBoardEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_sarcoma_boards Tabelle.
    Ein Sarkom-Board ist ein multidisziplinäres Tumor-Board zur Behandlungsplanung.
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")

    # Datum der Board-Präsentation (optional bei LLM-Extraktion)
    presentation_date: Optional[date] = Field(default=None, description="Datum der Board-Präsentation")

    # Grund und Status
    reason_for_presentation: Optional[ReasonForPresentation] = None
    status_before_follow_up: Optional[StatusBeforeFollowUp] = None
    status_after_follow_up: Optional[StatusAfterFollowUp] = None
    status_after_follow_up_comment: Optional[str] = Field(default=None, max_length=1000)

    # Behandlungsverlauf
    treatment_before_follow_up: Optional[TreatmentBeforeFollowUp] = None
    follow_up_reason: Optional[FollowUpReason] = None
    last_execution: Optional[LastExecution] = None
    unplanned_excision_date: Optional[date] = None

    # Fragestellung und Vorschlag
    question: Optional[str] = Field(default=None, max_length=2000, description="Fragestellung an das Board")
    proposed_procedure: Optional[str] = Field(default=None, max_length=2000, description="Vorgeschlagenes Vorgehen")

    # ECOG Performance Status (0-5)
    current_ecog: Optional[int] = Field(default=None, ge=0, le=5, description="ECOG Performance Status")

    # Board-Entscheidungen
    decision_surgery: Optional[BoardDecision] = None
    decision_surgery_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_radio_therapy: Optional[BoardDecision] = None
    decision_radio_therapy_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_systemic_therapy: Optional[BoardDecision] = None
    decision_systemic_therapy_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_follow_up: Optional[BoardDecision] = None
    decision_follow_up_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_diagnostics: Optional[BoardDecision] = None
    decision_diagnostics_comment: Optional[str] = Field(default=None, max_length=1000)

    decision_palliative_care: Optional[BoardDecision] = None
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
            # Entfernt mögliche Textanhänge
            s = s.split(' ')[0]
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        raise ValueError(f"Invalid date format: {v}")


class SarcomaBoardEvents(BaseModel):
    """
    Wrapper für mehrere Sarkom-Board-Events, extrahiert aus einem Bericht.
    """
    events: List[SarcomaBoardEvent]
