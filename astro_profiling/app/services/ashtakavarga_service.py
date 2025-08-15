from __future__ import annotations
import re
from pathlib import Path
from app.constants import ASHTAKA_SAVE_ROOT

def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")

def save_ashtakavarga_svg(svg_bytes: bytes, *,
                          name: str,
                          user_id: str,
                          phone_number: str,
                          chart_style: str,
                          dob: str,
                          tob: str) -> Path:
    """
    Folder: ashtakavarga_charts/<user_id>/
    File: <name>_<userId>_<phone>_sarvashtakavarga_<style>_<dob>_<tob>.svg
    """
    folder = ASHTAKA_SAVE_ROOT / _slug(user_id)
    folder.mkdir(parents=True, exist_ok=True)
    fname = f"{_slug(name)}_{_slug(user_id)}_{_slug(phone_number)}_sarvashtakavarga_{_slug(chart_style)}_{_slug(dob)}_{_slug(tob.replace(':','-'))}.svg"
    path = folder / fname
    path.write_bytes(svg_bytes)
    return path
