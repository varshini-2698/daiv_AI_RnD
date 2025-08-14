from __future__ import annotations
from prokerala_api import ApiClient  # pip install prokerala-api
from app.core.config import PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET

def prokerala_client() -> ApiClient:
    return ApiClient(PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET)

def fetch_chart_svg(*, chart_type: str, chart_style: str,
                    dob: str, tob: str, offset: str,
                    lat: float, lon: float) -> bytes:
    client = prokerala_client()
    result = client.get(
        "v2/astrology/chart",
        {
            "ayanamsa": 1,
            "coordinates": f"{lat},{lon}",
            "datetime": f"{dob}T{tob}{offset}",
            "chart_type": chart_type,
            "chart_style": chart_style,
            "format": "svg",
        },
    )
    if isinstance(result, (bytes, bytearray)):
        return bytes(result)
    raise RuntimeError("Unexpected provider response (expected SVG bytes)")
