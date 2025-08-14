from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.constants import SUPPORTED_STYLES
from app.models.schemas import DChartParsedRequest, DChartParsedResponse, DChartParsedRow
from app.services.prokerala_client import fetch_chart_svg
from app.services.dcharts_service import save_chart_svg
from app.services.parsers.south_indian_dcharts import parse_chart_cells_from_south_indian_svg, simple_summary_lines

router = APIRouter(prefix="", tags=["charts"])

@router.post("/dcharts-parsed", response_model=DChartParsedResponse)
def dcharts_parsed(req: DChartParsedRequest):
    if req.chart_style not in SUPPORTED_STYLES:
        raise HTTPException(status_code=422, detail=f"Unsupported chart_style: {req.chart_style}. Supported: {', '.join(SUPPORTED_STYLES)}")

    # Fetch SVG
    try:
        svg = fetch_chart_svg(
            chart_type=req.chart_type,
            chart_style=req.chart_style,
            dob=req.dob, tob=req.tob, offset=req.offset,
            lat=req.lat, lon=req.lon,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    # Save SVG (folder structure unchanged)
    try:
        _ = save_chart_svg(
            svg,
            name=req.name,
            user_id=req.user_id,
            phone_number=req.phone_number,
            chart_type=req.chart_type,
            chart_style=req.chart_style,
            dob=req.dob,
            tob=req.tob,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save SVG: {e}")

    # Parse chart → JSON
    try:
        rows = parse_chart_cells_from_south_indian_svg(svg)
    except Exception as e:
        rows = []  # safer fallback

    summary = simple_summary_lines(req.chart_type, rows)

    return DChartParsedResponse(
        # echo user info
        name=req.name,
        user_id=req.user_id,
        phone_number=req.phone_number,
        # chart info
        dchart=req.chart_type,
        chart_style=req.chart_style,
        chart_cells=[DChartParsedRow(**r) for r in rows],
        simple=summary,
    )
