from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import SAVRequest, SAVResponse, SAVSignTotal
from app.services.prokerala_client import fetch_chart_svg
from app.services.ashtakavarga_service import save_ashtakavarga_svg
from app.services.parsers.ashtakavarga_svg import parse_sav_totals_from_svg, simple_sav_lines

router = APIRouter(prefix="", tags=["ashtakavarga"])

@router.post("/ashtakavarga", response_model=SAVResponse)
def ashtakavarga(req: SAVRequest):
    # fetch SVG
    try:
        svg = fetch_chart_svg(
            chart_type="sarvashtakavarga-chart",   # endpoint path type is chart-ish; we still call dedicated path below via prokerala
            chart_style=req.chart_style,
            dob=req.dob, tob=req.tob, offset=req.offset,
            lat=req.lat, lon=req.lon,
        )
    except Exception as e:
        # If your prokerala client needs a different path for SAV, we can
        # add a dedicated fetch call; for now, we bubble error.
        raise HTTPException(status_code=502, detail=f"Provider error: {e}")

    # save SVG
    try:
        saved = save_ashtakavarga_svg(
            svg,
            name=req.name,
            user_id=req.user_id,
            phone_number=req.phone_number,
            chart_style=req.chart_style,
            dob=req.dob,
            tob=req.tob,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save SVG: {e}")

    # parse → totals
    try:
        rows = parse_sav_totals_from_svg(svg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse error: {e}")

    grand_total = sum(r["total"] for r in rows)
    simple = simple_sav_lines(rows)

    return SAVResponse(
        name=req.name,
        user_id=req.user_id,
        phone_number=req.phone_number,
        chart_style=req.chart_style,
        totals=[SAVSignTotal(**r) for r in rows],
        grand_total=grand_total,
        simple=simple,
        file_path=str(saved),
    )
