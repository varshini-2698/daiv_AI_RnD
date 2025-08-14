from pathlib import Path
import os

# Supported chart styles for current parser(s)
SUPPORTED_STYLES = {"south-indian"}

# Zodiac sign names (1..12)
SIGN_NAMES = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}

# Planet abbreviations -> full names (used in SVG)
PLANET_MAP = {
    "Asc": "Ascendant",
    "Su": "Sun", "Mo": "Moon", "Ma": "Mars", "Me": "Mercury",
    "Ju": "Jupiter", "Ve": "Venus", "Sa": "Saturn",
    "Ra": "Rahu", "Ke": "Ketu",
}

# Storage root for saved charts (folder structure unchanged)
SAVE_ROOT = Path(os.getenv("DCHARTS_SAVE_DIR", "./charts")).resolve()
