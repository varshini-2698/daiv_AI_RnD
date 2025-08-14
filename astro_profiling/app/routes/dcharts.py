# from __future__ import annotations
# from fastapi import APIRouter, HTTPException
# from app.constants import SUPPORTED_STYLES
# from app.models.schemas import DChartParsedRequest, DChartParsedResponse, DChartParsedRow
# from app.services.prokerala_client import fetch_chart_svg
# from app.services.dcharts_service import save_chart_svg
# from app.services.parsers.south_indian_dcharts import parse_chart_cells_from_south_indian_svg, simple_summary_lines

# router = APIRouter(prefix="", tags=["charts"])

# @router.post("/dcharts-parsed", response_model=DChartParsedResponse)
# def dcharts_parsed(req: DChartParsedRequest):
#     if req.chart_style not in SUPPORTED_STYLES:
#         raise HTTPException(status_code=422, detail=f"Unsupported chart_style: {req.chart_style}. Supported: {', '.join(SUPPORTED_STYLES)}")

#     # Fetch SVG
#     try:
#         svg = fetch_chart_svg(
#             chart_type=req.chart_type,
#             chart_style=req.chart_style,
#             dob=req.dob, tob=req.tob, offset=req.offset,
#             lat=req.lat, lon=req.lon,
#         )
#     except Exception as e:
#         raise HTTPException(status_code=502, detail=f"Provider error: {e}")

#     # Save SVG (folder structure unchanged)
#     try:
#         _ = save_chart_svg(
#             svg,
#             name=req.name,
#             user_id=req.user_id,
#             phone_number=req.phone_number,
#             chart_type=req.chart_type,
#             chart_style=req.chart_style,
#             dob=req.dob,
#             tob=req.tob,
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save SVG: {e}")

#     # Parse chart → JSON
#     try:
#         rows = parse_chart_cells_from_south_indian_svg(svg)
#     except Exception as e:
#         rows = []  # safer fallback

#     summary = simple_summary_lines(req.chart_type, rows)

#     return DChartParsedResponse(
#         # echo user info
#         name=req.name,
#         user_id=req.user_id,
#         phone_number=req.phone_number,
#         # chart info
#         dchart=req.chart_type,
#         chart_style=req.chart_style,
#         chart_cells=[DChartParsedRow(**r) for r in rows],
#         simple=summary,
#     )
from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException
from app.constants import SUPPORTED_STYLES, ALL_DCHART_TYPES
from app.models.schemas import DChartsAllRequest, DChartsAllResponse, DChartParsedRow
from app.services.prokerala_client import fetch_chart_svg
from app.services.dcharts_service import save_chart_svg, save_user_text, save_user_json_txt
from app.services.parsers.south_indian_dcharts import parse_chart_cells_from_south_indian_svg, simple_summary_lines

router = APIRouter(prefix="", tags=["charts"])

@router.post("/dcharts-parsed/all", response_model=DChartsAllResponse)
def dcharts_parsed_all(req: DChartsAllRequest):
    if req.chart_style not in SUPPORTED_STYLES:
        raise HTTPException(status_code=422, detail=f"Unsupported chart_style: {req.chart_style}. Supported: {', '.join(SUPPORTED_STYLES)}")

    dcharts_json = {}       # { dchart_name: [ {no, sign_name, planets}, ... ] }
    all_summary_lines = []  # ["DCHART=RASI", "Jupiter...", "DCHART=NAVAMSA", ... ]

    # Iterate over EVERY D-chart type
    for dchart in ALL_DCHART_TYPES:
        # 1) Fetch SVG
        try:
            svg = fetch_chart_svg(
                chart_type=dchart,
                chart_style=req.chart_style,
                dob=req.dob, tob=req.tob, offset=req.offset,
                lat=req.lat, lon=req.lon,
            )
        except Exception as e:
            # Skip this chart on provider failure, but continue others
            dcharts_json[dchart] = []
            all_summary_lines.append(f"DCHART={dchart.upper()} (error: {e})")
            continue

        # 2) Save SVG (side-effect)
        try:
            _ = save_chart_svg(
                svg,
                name=req.name,
                user_id=req.user_id,
                phone_number=req.phone_number,
                chart_type=dchart,
                chart_style=req.chart_style,
                dob=req.dob,
                tob=req.tob,
            )
        except Exception as e:
            # Still continue parsing if save fails
            all_summary_lines.append(f"DCHART={dchart.upper()} (save error: {e})")

        # 3) Parse → JSON table
        try:
            rows = parse_chart_cells_from_south_indian_svg(svg)
        except Exception as e:
            rows = []
            all_summary_lines.append(f"DCHART={dchart.upper()} (parse error: {e})")

        dcharts_json[dchart] = rows
        # 4) Append human-readable lines for this chart
        all_summary_lines.extend(simple_summary_lines(dchart, rows))

    # 5) Save two txt files for this user
    summary_path = save_user_text(
        req.name, req.user_id, req.phone_number,
        filename_suffix="ALL_dcharts_summary",
        content="\n".join(all_summary_lines),
    )
    json_txt_path = save_user_json_txt(
        req.name, req.user_id, req.phone_number,
        filename_suffix="ALL_dcharts",
        data=dcharts_json,
    )

    # 6) Return combined JSON (no SVGs, just parsed content + file paths)
    #    Convert dict of lists into pydantic-friendly structure
    dcharts_response = {k: [DChartParsedRow(**r) for r in v] for k, v in dcharts_json.items()}

    return DChartsAllResponse(
        name=req.name,
        user_id=req.user_id,
        phone_number=req.phone_number,
        chart_style=req.chart_style,
        dcharts=dcharts_response,
        simple=all_summary_lines,
        files={
            "summary_txt": str(summary_path),
            "json_txt": str(json_txt_path)
        }
    )
