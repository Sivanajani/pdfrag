from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class SurgeryIndication(str, Enum):
    preoperative_biopsy = "Preoperative biopsy"
    definitive_surgery = "Definitive surgery"
    curative_resection = "Curative resection"
    palliative_surgery = "Palliative surgery"
    revision_surgery = "Revision surgery"
    debulking = "Debulking"
    metastasectomy = "Metastasectomy"
    other = "Other"


class SurgerySide(str, Enum):
    left = "Left"
    right = "Right"
    bilateral = "Bilateral"
    midline = "Midline"
    not_applicable = "Not applicable"


class AnatomicRegion(str, Enum):
    head_neck = "Head and neck"
    trunk = "Trunk"
    chest_wall = "Chest wall"
    abdomen = "Abdomen"
    pelvis = "Pelvis"
    upper_extremity = "Upper extremity"
    lower_extremity = "Lower extremity"
    retroperitoneum = "Retroperitoneum"
    other = "Other"


class ResectionType(str, Enum):
    wide_excision = "Wide excision"
    marginal_excision = "Marginal excision"
    intralesional_excision = "Intralesional excision"
    compartmental_resection = "Compartmental resection"
    en_bloc_resection = "En-bloc resection"
    limb_sparing = "Limb-sparing surgery"


class ReconstructionType(str, Enum):
    none = "None"
    primary_closure = "Primary closure"
    skin_graft = "Skin graft"
    local_flap = "Local flap"
    free_flap = "Free flap"
    mesh = "Mesh"
    prosthesis = "Prosthesis"
    bone_graft = "Bone graft"
    endoprosthesis = "Endoprosthesis"
    other = "Other"


class AmputationType(str, Enum):
    none = "None"
    above_knee = "Above-knee amputation"
    below_knee = "Below-knee amputation"
    above_elbow = "Above-elbow amputation"
    below_elbow = "Below-elbow amputation"
    hip_disarticulation = "Hip disarticulation"
    shoulder_disarticulation = "Shoulder disarticulation"
    hemipelvectomy = "Hemipelvectomy"
    other = "Other"


class SurgicalMargin(str, Enum):
    r0 = "R0 (complete resection, negative margins)"
    r1 = "R1 (microscopic residual tumor)"
    r2 = "R2 (macroscopic residual tumor)"
    unknown = "Unknown"


class ParticipatedDiscipline(str, Enum):
    orthopedic_surgery = "Orthopedic surgery"
    general_surgery = "General surgery"
    plastic_surgery = "Plastic surgery"
    vascular_surgery = "Vascular surgery"
    thoracic_surgery = "Thoracic surgery"
    neurosurgery = "Neurosurgery"
    gynecology = "Gynecology"
    urology = "Urology"
    other = "Other"


class SurgeryEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_surgeries Tabelle.
    """

    institution_id: Optional[int] = Field(default=None, ge=0, description="Institution ID")
    patient_id: Optional[int] = Field(default=None, ge=0, description="Patient ID")
    responsible_surgeon_id: Optional[int] = Field(default=None, ge=0, description="Verantwortlicher Chirurg")

    # Datum der Operation (optional bei LLM-Extraktion)
    surgery_date: Optional[date] = Field(default=None, description="Datum der Operation")

    # Operations-Details
    indication: Optional[SurgeryIndication] = None
    indication_comment: Optional[str] = Field(default=None, max_length=1000)

    surgery_side: Optional[SurgerySide] = None
    anatomic_region: Optional[AnatomicRegion] = None

    # Tumor-Charakteristika
    greatest_surgical_tumor_dimension_in_mm: Optional[int] = Field(
        default=None,
        ge=0,
        description="Größte Tumordimension in mm"
    )
    had_tumor_spillage: Optional[bool] = Field(
        default=None,
        description="Tumor-Spillage während der OP"
    )

    # Resektions-Details
    resection: List[ResectionType] = Field(
        default_factory=list,
        description="Art der Resektion (mehrere möglich)"
    )
    resected_tumor_margin: Optional[SurgicalMargin] = None

    # Rekonstruktion und Amputation
    reconstruction: Optional[ReconstructionType] = None
    amputation: Optional[AmputationType] = None
    hemipelvectomy: List[str] = Field(
        default_factory=list,
        description="Hemipelvektomie-Details (falls zutreffend)"
    )

    # Revisionen
    first_revision_details: Optional[str] = Field(default=None, max_length=500)
    second_revision_details: Optional[str] = Field(default=None, max_length=500)

    # Beteiligte Disziplinen
    participated_disciplines: List[ParticipatedDiscipline] = Field(
        default_factory=list,
        description="Beteiligte Fachdisziplinen"
    )
    participated_disciplines_comment: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("surgery_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """
        Parst flexible Datumsformate (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
        """
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("surgery_date is required")

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

        raise ValueError(f"Invalid date format: {v}")


class SurgeryEvents(BaseModel):
    """
    Wrapper für mehrere Chirurgie-Events, extrahiert aus einem Bericht.
    """
    events: List[SurgeryEvent]
