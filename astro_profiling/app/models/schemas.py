from __future__ import annotations

import re
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, field_validator

from app.constants import ALLOWED_TYPES, ALLOWED_STYLES


class DChartRequest(BaseModel):
    dob: str = Field(..., description="YYYY-MM-DD")
    tob: str = Field(..., description="HH:MM or HH:MM:SS in local time")
    offset: str = Field(..., description="Timezone offset like +05:30 or -04:00")
    lat: float
    lon: float
    chart_type: str
    chart_style: str = "south-indian"

    # Optional metadata
    name: Optional[str] = None
    phone_number: Optional[str] = None
    user_id: Optional[str] = None

    # Return mode
    return_: Literal["file", "inline"] = Field("file", alias="return")

    @field_validator("dob")
    @classmethod
    def _validate_dob(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("dob must be YYYY-MM-DD")
        return v

    @field_validator("tob")
    @classmethod
    def _validate_tob(cls, v: str) -> str:
        if re.fullmatch(r"\d{2}:\d{2}", v):
            return f"{v}:00"
        if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", v):
            raise ValueError("tob must be HH:MM or HH:MM:SS")
        return v

    @field_validator("offset")
    @classmethod
    def _validate_offset(cls, v: str) -> str:
        if not re.fullmatch(r"[+-]\d{2}:\d{2}", v):
            raise ValueError("offset must be like +05:30 or -04:00")
        return v

    @field_validator("chart_type")
    @classmethod
    def _validate_chart_type(cls, v: str) -> str:
        if v not in ALLOWED_TYPES:
            raise ValueError(f"chart_type must be one of {ALLOWED_TYPES}")
        return v

    @field_validator("chart_style")
    @classmethod
    def _validate_chart_style(cls, v: str) -> str:
        if v not in ALLOWED_STYLES:
            raise ValueError(f"chart_style must be one of {ALLOWED_STYLES}")
        return v


class DChartFileResult(BaseModel):
    path: str
    filename: str
    absolute_path: str


class ChartTypesResponse(BaseModel):
    chart_types: List[str]
    chart_styles: List[str]
