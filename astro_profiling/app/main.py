from fastapi import FastAPI
from app.routes.dcharts import router as parsed_router
from app.routes.ashtakavarga import router as sav_router

app = FastAPI(
    title="Astro Charts Parser API",
    version="1.0.0",
    description="Fetch, store SVG (charts only), and return parsed chart JSON + simple summary."
)

app.include_router(parsed_router)
app.include_router(sav_router)