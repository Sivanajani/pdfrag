from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class TimingOfImaging(str, Enum):
    initial = "Initial imaging"
    follow_up = "Follow-up imaging"


class TypeOfImaging(str, Enum):
    local = "Local imaging"
    systemic = "Systemic imaging"


class RadiologyExamType(str, Enum):
    xray = "conventional X-Ray"
    mri = "MRI"
    ct = "CT scan"
    us = "Ultrasound (US)"
    pet_ct = "PET-CT"
    pet_mri = "PET-MRI"
    scintigraphy = "Scintigraphy"
    other = "Other"


class LocationOfLesion(str, Enum):
    head_neck = "Head and neck"
    trunk = "Trunk"
    chest = "Chest"
    abdomen = "Abdomen"
    pelvis = "Pelvis"
    upper_extremity = "Upper extremity"
    lower_extremity = "Lower extremity"
    retroperitoneum = "Retroperitoneum"
    multiple = "Multiple locations"
    other = "Other"


class RECISTResponse(str, Enum):
    complete_response = "CR (Complete Response)"
    partial_response = "PR (Partial Response)"
    stable_disease = "SD (Stable Disease)"
    progressive_disease = "PD (Progressive Disease)"
    not_evaluable = "NE (Not Evaluable)"


class ChoiResponse(str, Enum):
    complete_response = "CR (Complete Response)"
    partial_response = "PR (Partial Response)"
    stable_disease = "SD (Stable Disease)"
    progressive_disease = "PD (Progressive Disease)"


class iRECISTResponse(str, Enum):
    immune_complete_response = "iCR (immune Complete Response)"
    immune_partial_response = "iPR (immune Partial Response)"
    immune_stable_disease = "iSD (immune Stable Disease)"
    immune_progressive_disease = "iPD (immune Progressive Disease)"
    immune_unconfirmed_progressive_disease = "iUPD (immune Unconfirmed PD)"


class PETResponse(str, Enum):
    complete_metabolic_response = "CMR (Complete Metabolic Response)"
    partial_metabolic_response = "PMR (Partial Metabolic Response)"
    stable_metabolic_disease = "SMD (Stable Metabolic Disease)"
    progressive_metabolic_disease = "PMD (Progressive Metabolic Disease)"


class LocalDiseaseStatus(str, Enum):
    no_disease = "No disease"
    measurable = "Measurable"
    non_measurable = "Non-measurable"
    unknown = "Unknown"


class LocalDiseaseMeasurable(str, Enum):
    yes = "Yes"
    no = "No"
    unknown = "Unknown"


class QualitativeMRIResponse(str, Enum):
    complete_response = "Complete response"
    partial_response = "Partial response"
    stable_disease = "Stable disease"
    progressive_disease = "Progressive disease"


class MetastasisStatus(str, Enum):
    no_metastasis = "No metastasis"
    metastasis_present = "Metastasis present"
    indeterminate = "Indeterminate"
    unknown = "Unknown"


class AnatomicLocationOfMetastasis(str, Enum):
    lung = "Lung"
    pleura = "Pleura"
    bone = "Bone"
    liver = "Liver"
    soft_tissue = "Soft tissue"
    lymph_node = "Lymph node"
    brain = "Brain"
    peritoneum = "Peritoneum"
    other = "Other"


class MetastasisCount(str, Enum):
    none = "0"
    one = "1"
    two = "2"
    three = "3"
    four_to_ten = "4-10"
    more_than_ten = ">10"
    numerous = "Numerous"
    unknown = "Unknown"


class MetastasisIndeterminateCategory(str, Enum):
    probably_benign = "Probably benign"
    indeterminate = "Indeterminate"
    suspicious = "Suspicious"


class RadiologyEvent(BaseModel):
    """
    Repräsentiert eine Zeile aus der croms_radiology_exams Tabelle.
    Enthält alle Felder für vollständige Radiology-Befunde.
    """

    # IDs (in DB nicht nullable, aber hier optional für LLM-Extraktion)
    institution_id: Optional[int] = Field(default=None, ge=0)
    patient_id: Optional[int] = Field(default=None, ge=0)

    # Datum (optional — LLM liefert nicht immer ein Datum)
    exam_date: Optional[date] = Field(default=None, description="Untersuchungsdatum")

    # Grundlegende Untersuchungs-Informationen
    exam_type: Optional[RadiologyExamType] = None
    exam_type_comment: Optional[str] = Field(default=None, max_length=2000)
    imaging_timing: Optional[TimingOfImaging] = None
    imaging_type: Optional[TypeOfImaging] = None

    # Läsions-Informationen
    location_of_lesion: Optional[LocationOfLesion] = None
    largest_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)
    medium_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)
    smallest_lesion_size_in_mm: Optional[int] = Field(default=None, ge=0)

    # Response-Kriterien
    recist_response: Optional[RECISTResponse] = None
    choi_response: Optional[ChoiResponse] = None
    irecist_response: Optional[iRECISTResponse] = None
    pet_response: Optional[PETResponse] = None

    # Lokale Erkrankung
    local_disease_status: Optional[LocalDiseaseStatus] = None
    local_disease_measurable: Optional[LocalDiseaseMeasurable] = None
    local_disease_report_largest_diameter: Optional[int] = Field(
        default=None,
        ge=0,
        description="Größter Durchmesser der lokalen Läsion in mm"
    )
    local_disease_qualitative_mri_response: Optional[QualitativeMRIResponse] = None
    local_disease_radiologist_confidence: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Radiologist confidence level (1-5)"
    )
    local_disease_pet_metabolic_response: Optional[PETResponse] = None

    # Metastasen - Allgemein
    metastasis_presence: Optional[bool] = Field(
        default=None,
        description="Metastasen vorhanden? (deprecated, use metastasis field)"
    )
    metastasis: Optional[MetastasisStatus] = None
    anatomic_location_of_metastasis: List[AnatomicLocationOfMetastasis] = Field(
        default_factory=list,
        description="Anatomische Lokalisationen der Metastasen (Array)"
    )

    # Metastasen - Lokalisation mit Anzahl
    metastasis_location_lung_count: Optional[MetastasisCount] = None
    metastasis_location_pleura_count: Optional[MetastasisCount] = None
    metastasis_location_bone_count: Optional[MetastasisCount] = None
    metastasis_location_liver_count: Optional[MetastasisCount] = None
    metastasis_location_soft_tissue_count: Optional[MetastasisCount] = None
    metastasis_location_lymph_node_count: Optional[MetastasisCount] = None
    metastasis_location_brain_count: Optional[MetastasisCount] = None
    metastasis_location_other_count: Optional[MetastasisCount] = None

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
    metastasis_indeterminate_category: Optional[MetastasisIndeterminateCategory] = None

    # Befundtext und Datum
    radiology_report: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Vollständiger Radiologie-Befundtext"
    )
    report_date: Optional[date] = Field(default=None, description="Befunddatum")

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
