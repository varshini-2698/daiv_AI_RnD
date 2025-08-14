from __future__ import annotations

import re
from pathlib import Path
from fastapi import HTTPException

from app.core.config import DCHARTS_SAVE_DIR
from app.services.prokerala_client import get_api_client


def _safe_slug(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")


def fetch_chart_svg(*,
                    chart_type: str,
                    chart_style: str,
                    dob: str,
                    tob: str,
                    offset: str,
                    lat: float,
                    lon: float) -> bytes:
    """
    Calls Prokerala chart API and returns raw SVG bytes.
    """
    client = get_api_client()
    api_path = "v2/astrology/chart"
    params = {
        "ayanamsa": 1,  # Lahiri
        "coordinates": f"{lat},{lon}",
        "datetime": f"{dob}T{tob}{offset}",
        "chart_type": chart_type,
        "chart_style": chart_style,
        "format": "svg",
    }
    result = client.get(api_path, params)

    if isinstance(result, (bytes, bytearray)):
        return bytes(result)

    raise HTTPException(
        status_code=502,
        detail={"message": "Unexpected response from provider", "type": str(type(result))}
    )


def save_svg(svg_bytes: bytes, *,
             user_id: str | None,
             chart_type: str,
             chart_style: str,
             dob: str,
             tob: str,
             name: str | None) -> Path:
    user_dir = DCHARTS_SAVE_DIR / _safe_slug(user_id or "anon")
    user_dir.mkdir(parents=True, exist_ok=True)

    fname = f"{chart_type}_{chart_style}_{dob}_{tob.replace(':','-')}"
    if name:
        fname = f"{_safe_slug(name)}_{fname}"
    path = user_dir / f"{fname}.svg"
    path.write_bytes(svg_bytes)
    return path
