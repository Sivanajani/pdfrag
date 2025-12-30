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


class RadiologyEvent(BaseModel):
    """
    One row from MDS_Radiology = one radiology/interventional event.
    """

    institution_id: int = Field(..., ge=0)
    patient_id: int = Field(..., ge=0)

    exam_date: date

    imaging_timing: Optional[TimingOfImaging] = None
    imaging_scope: Optional[TypeOfImaging] = None
    exam_type: Optional[RadiologyExamType] = None

    interventional_method: Optional[str] = Field(default=None, max_length=255)

    @field_validator("exam_date", mode="before")
    @classmethod
    def parse_exam_date(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("exam_date is required")

        if isinstance(v, date):
            return v

        if isinstance(v, str):
            s = v.strip()
            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt).date()
                except ValueError:
                    pass

        raise ValueError(f"Invalid exam_date format: {v}")


class RadiologyEvents(BaseModel):
    """
    Wrapper for multiple radiology events extracted from one report.
    """
    events: List[RadiologyEvent]
