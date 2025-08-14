from __future__ import annotations
import re
from typing import List
from pydantic import BaseModel, Field, field_validator

class DChartParsedRow(BaseModel):
    no: int
    sign_name: str
    planets: List[str]

class DChartParsedResponse(BaseModel):
    # user info echoed back
    name: str
    user_id: str
    phone_number: str

    # chart info
    dchart: str               # "rasi", "navamsa", ...
    chart_style: str          # "south-indian"
    chart_cells: List[DChartParsedRow]

    # human readable block
    simple: str

class DChartParsedRequest(BaseModel):
    # required user info
    name: str
    user_id: str
    phone_number: str

    # required chart request
    dob: str = Field(..., description="YYYY-MM-DD")
    tob: str = Field(..., description="HH:MM or HH:MM:SS local time")
    offset: str = Field(..., description="+05:30, -04:00 etc.")
    lat: float
    lon: float
    chart_type: str = Field(..., description="rasi/navamsa/drekkana/...")
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