import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")

if not PROKERALA_CLIENT_ID or not PROKERALA_CLIENT_SECRET:
    raise RuntimeError(
        "Missing PROKERALA_CLIENT_ID/PROKERALA_CLIENT_SECRET. "
        "Create a .env with those keys."
    )

DCHARTS_SAVE_DIR = Path(os.getenv("DCHARTS_SAVE_DIR", "./charts")).resolve()
DCHARTS_SAVE_DIR.mkdir(parents=True, exist_ok=True)

ALLOW_ORIGINS = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "*").split(",") if o.strip()]
