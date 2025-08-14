from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOW_ORIGINS
from app.routes.dcharts import router as dcharts_router

app = FastAPI(
    title="DCharts Service",
    version="1.0.0",
    description="Fetch Prokerala divisional (D) charts as SVG via FastAPI.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS if ALLOW_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(dcharts_router)
