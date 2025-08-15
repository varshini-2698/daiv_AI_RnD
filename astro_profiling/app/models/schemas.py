from __future__ import annotations

import re
from typing import List, Dict

from pydantic import BaseModel, Field, field_validator
class DChartParsedRow(BaseModel):
    no: int
    sign_name: str
    planets: List[str]

# Generate ALL D-charts request/response
class DChartsAllRequest(BaseModel):
    # required user info
    name: str
    user_id: str
    phone_number: str

    # required birth/loc info
    dob: str = Field(..., description="YYYY-MM-DD")
    tob: str = Field(..., description="HH:MM or HH:MM:SS local time")
    offset: str = Field(..., description="+05:30, -04:00 etc.")
    lat: float
    lon: float

    # style (we currently parse South-Indian)
    chart_style: str = Field("south-indian", description="currently supports south-indian")

    @field_validator("dob")
    @classmethod
    def _vdob(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("dob must be YYYY-MM-DD")
        return v

    @field_validator("tob")
    @classmethod
    def _vtob(cls, v: str) -> str:
        if re.fullmatch(r"\d{2}:\d{2}", v):
            return f"{v}:00"
        if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", v):
            raise ValueError("tob must be HH:MM or HH:MM:SS")
        return v

    @field_validator("offset")
    @classmethod
    def _voffset(cls, v: str) -> str:
        if not re.fullmatch(r"[+-]\d{2}:\d{2}", v):
            raise ValueError("offset must be like +05:30 or -04:00")
        return v

class DChartsAllResponse(BaseModel):
    # Echo user
    name: str
    user_id: str
    phone_number: str

    # Style
    chart_style: str

    # Parsed results for ALL D-charts: { "rasi": [...], "navamsa": [...], ... }
    dcharts: Dict[str, List[DChartParsedRow]]

    # A single human-readable block (one-liners for all charts)
    simple: List[str]

    # Saved artifacts
    files: Dict[str, str]  # {"summary_txt": "...path...", "json_txt": "...path..."}

# ----- Ashtakavarga (SAV) -----

class SAVSignTotal(BaseModel):
    no: int
    sign_name: str
    total: int

class SAVRequest(BaseModel):
    # required user info
    name: str
    user_id: str
    phone_number: str

    # required birth/loc info
    dob: str = Field(..., description="YYYY-MM-DD")
    tob: str = Field(..., description="HH:MM or HH:MM:SS local time")
    offset: str = Field(..., description="+05:30, -04:00 etc.")
    lat: float
    lon: float

    # style for chart rendering (Prokerala supports south/east for this endpoint)
    chart_style: str = Field("south-indian", description="south-indian or east-indian")

    @field_validator("dob")
    @classmethod
    def _vdob(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("dob must be YYYY-MM-DD")
        return v

    @field_validator("tob")
    @classmethod
    def _vtob(cls, v: str) -> str:
        if re.fullmatch(r"\d{2}:\d{2}", v):
            return f"{v}:00"
        if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", v):
            raise ValueError("tob must be HH:MM or HH:MM:SS")
        return v

    @field_validator("offset")
    @classmethod
    def _voffset(cls, v: str) -> str:
        if not re.fullmatch(r"[+-]\d{2}:\d{2}", v):
            raise ValueError("offset must be like +05:30 or -04:00")
        return v

class SAVResponse(BaseModel):
    # echo user
    name: str
    user_id: str
    phone_number: str

    # chart style
    chart_style: str

    # parsed totals
    totals: List[SAVSignTotal]      # 12 rows
    grand_total: int

    # human-readable lines
    simple: List[str]

    # saved file path
    file_path: str
