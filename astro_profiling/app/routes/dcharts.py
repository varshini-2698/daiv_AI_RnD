from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse

from app.constants import ALLOWED_TYPES, ALLOWED_STYLES
from app.models.schemas import (
    DChartRequest,
    DChartFileResult,
    ChartTypesResponse,
)
from app.services.dcharts_service import fetch_chart_svg, save_svg

router = APIRouter(prefix="", tags=["dcharts"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/chart-types", response_model=ChartTypesResponse)
def chart_types() -> ChartTypesResponse:
    return ChartTypesResponse(chart_types=ALLOWED_TYPES, chart_styles=ALLOWED_STYLES)


@router.post("/dcharts")
def generate_dchart(req: DChartRequest):
    if req.chart_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail=f"Unsupported chart_type: {req.chart_type}")
    if req.chart_style not in ALLOWED_STYLES:
        raise HTTPException(status_code=422, detail=f"Unsupported chart_style: {req.chart_style}")

    try:
        svg = fetch_chart_svg(
            chart_type=req.chart_type,
            chart_style=req.chart_style,
            dob=req.dob,
            tob=req.tob,
            offset=req.offset,
            lat=req.lat,
            lon=req.lon,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    if req.return_ == "inline":
        return Response(content=svg, media_type="image/svg+xml")

    saved = save_svg(
        svg,
        user_id=req.user_id,
        chart_type=req.chart_type,
        chart_style=req.chart_style,
        dob=req.dob,
        tob=req.tob,
        name=req.name,
    )
    return JSONResponse(
        DChartFileResult(
            path=str(saved),
            filename=saved.name,
            absolute_path=str(saved.resolve()),
        ).model_dump()
    )
