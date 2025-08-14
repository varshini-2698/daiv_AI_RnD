from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
from app.constants import SIGN_NAMES, PLANET_MAP

def _extract_text_nodes(svg_text: str) -> List[Dict]:
    safe_svg = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
    root = ET.fromstring(safe_svg)
    out: List[Dict] = []
    for t in root.findall(".//{http://www.w3.org/2000/svg}text"):
        x, y = t.get("x"), t.get("y")
        if not x or not y: continue
        content = "".join(t.itertext()).strip()
        if not content: continue
        try:
            xf, yf = float(x), float(y)
        except ValueError:
            continue
        out.append({"x": xf, "y": yf, "text": content, "class": t.get("class") or ""})
    return out

def _grid_from_lines(svg_text: str) -> Tuple[list[float], list[float]]:
    safe_svg = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
    root = ET.fromstring(safe_svg)
    xs, ys = set(), set()
    for ln in root.findall(".//{http://www.w3.org/2000/svg}line"):
        x1, y1, x2, y2 = ln.get("x1"), ln.get("y1"), ln.get("x2"), ln.get("y2")
        if not all([x1, y1, x2, y2]): continue
        x1f, y1f, x2f, y2f = float(x1), float(y1), float(x2), float(y2)
        if abs(x1f - x2f) < 1e-3: xs.add(round(x1f, 3))
        if abs(y1f - y2f) < 1e-3: ys.add(round(y1f, 3))
    return sorted(xs), sorted(ys)

def _cell_index(x: float, y: float, xs: list[float], ys: list[float]) -> Optional[tuple[int,int]]:
    def idx(v, arr):
        for i in range(len(arr) - 1):
            if arr[i] <= v <= arr[i + 1]:
                return i
        return None
    ci, ri = idx(x, xs), idx(y, ys)
    return (ci, ri) if (ci is not None and ri is not None) else None

def _planet_label_to_full(abbr: str) -> str:
    return f"{PLANET_MAP.get(abbr, abbr)} ({abbr})"

def parse_chart_cells_from_south_indian_svg(svg_bytes: bytes) -> list[dict]:
    """
    Parse ANY South-Indian divisional chart (rasi/navamsa/...) into 12 rows.
    Returns: [{"no", "sign_name", "planets":[...]}]
    """
    svg_text = svg_bytes.decode("utf-8")
    xs, ys = _grid_from_lines(svg_text)
    texts = _extract_text_nodes(svg_text)

    # Map each cell to its house/sign number using labels "1".."12"
    cell_to_no: Dict[tuple[int,int], int] = {}
    for n in texts:
        txt = n["text"]
        if txt.isdigit():
            v = int(txt)
            if 1 <= v <= 12:
                k = _cell_index(n["x"], n["y"], xs, ys)
                if k: cell_to_no[k] = v

    # Collect planets in each numbered cell
    known = set(PLANET_MAP.keys())
    no_to_planets: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
    for n in texts:
        t = n["text"]
        if t in known:
            k = _cell_index(n["x"], n["y"], xs, ys)
            if k and k in cell_to_no:
                no_to_planets[cell_to_no[k]].append(_planet_label_to_full(t))

    # Build ordered rows 1..12
    rows: List[dict] = []
    for no in range(1, 13):
        rows.append({
            "no": no,
            "sign_name": SIGN_NAMES.get(no, f"Sign {no}"),
            "planets": no_to_planets[no] or [],
        })
    return rows

def simple_summary_lines(dchart: str, rows: list[dict]) -> list[str]:
    """
    Returns array of one-liners for a single chart.
    e.g., ["DCHART=RASI", "Jupiter, Saturn in Aries", ...]
    """
    out = [f"DCHART={dchart.upper()}"]
    for row in rows:
        if not row["planets"]:
            continue
        names = [p.split(" (")[0] for p in row["planets"]]
        out.append(f"{', '.join(names)} in {row['sign_name']}")
    return out


# from __future__ import annotations
# import re
# import xml.etree.ElementTree as ET
# from typing import List, Dict, Optional, Tuple
# from app.constants import SIGN_NAMES, PLANET_MAP

# def _extract_text_nodes(svg_text: str) -> List[Dict]:
#     safe_svg = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
#     root = ET.fromstring(safe_svg)
#     out: List[Dict] = []
#     for t in root.findall(".//{http://www.w3.org/2000/svg}text"):
#         x, y = t.get("x"), t.get("y")
#         if not x or not y: continue
#         content = "".join(t.itertext()).strip()
#         if not content: continue
#         try:
#             xf, yf = float(x), float(y)
#         except ValueError:
#             continue
#         out.append({"x": xf, "y": yf, "text": content, "class": t.get("class") or ""})
#     return out

# def _grid_from_lines(svg_text: str) -> Tuple[list[float], list[float]]:
#     safe_svg = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
#     root = ET.fromstring(safe_svg)
#     xs, ys = set(), set()
#     for ln in root.findall(".//{http://www.w3.org/2000/svg}line"):
#         x1, y1, x2, y2 = ln.get("x1"), ln.get("y1"), ln.get("x2"), ln.get("y2")
#         if not all([x1, y1, x2, y2]): continue
#         x1f, y1f, x2f, y2f = float(x1), float(y1), float(x2), float(y2)
#         if abs(x1f - x2f) < 1e-3: xs.add(round(x1f, 3))
#         if abs(y1f - y2f) < 1e-3: ys.add(round(y1f, 3))
#     return sorted(xs), sorted(ys)

# def _cell_index(x: float, y: float, xs: list[float], ys: list[float]) -> Optional[tuple[int,int]]:
#     def idx(v, arr):
#         for i in range(len(arr) - 1):
#             if arr[i] <= v <= arr[i + 1]:
#                 return i
#         return None
#     ci, ri = idx(x, xs), idx(y, ys)
#     return (ci, ri) if (ci is not None and ri is not None) else None

# def _planet_label_to_full(abbr: str) -> str:
#     return f"{PLANET_MAP.get(abbr, abbr)} ({abbr})"

# def parse_chart_cells_from_south_indian_svg(svg_bytes: bytes) -> list[dict]:
#     """
#     Parse ANY South-Indian divisional chart (rasi/navamsa/...) into
#     12 rows: {"no", "sign_name", "planets":[...]}.
#     """
#     svg_text = svg_bytes.decode("utf-8")
#     xs, ys = _grid_from_lines(svg_text)
#     texts = _extract_text_nodes(svg_text)

#     # Map each cell to its house/sign number using labels "1".."12"
#     cell_to_no: Dict[tuple[int,int], int] = {}
#     for n in texts:
#         txt = n["text"]
#         if txt.isdigit():
#             v = int(txt)
#             if 1 <= v <= 12:
#                 k = _cell_index(n["x"], n["y"], xs, ys)
#                 if k: cell_to_no[k] = v

#     # Collect planets in each numbered cell
#     known = set(PLANET_MAP.keys())
#     no_to_planets: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
#     for n in texts:
#         t = n["text"]
#         if t in known:
#             k = _cell_index(n["x"], n["y"], xs, ys)
#             if k and k in cell_to_no:
#                 no_to_planets[cell_to_no[k]].append(_planet_label_to_full(t))

#     # Build ordered rows 1..12
#     rows: List[dict] = []
#     for no in range(1, 13):
#         rows.append({
#             "no": no,
#             "sign_name": SIGN_NAMES.get(no, f"Sign {no}"),
#             "planets": no_to_planets[no] or [],
#         })
#     return rows

# def simple_summary_lines(dchart: str, rows: list[dict]) -> str:
#     """
#     Example:
#       DCHART=RASI
#       Jupiter, Saturn in Aries
#       Sun, Mercury, Rahu in Cancer
#       ...
#     """
#     lines = [f"DCHART={dchart.upper()}"]
#     for row in rows:
#         if not row["planets"]:
#             continue
#         names = [p.split(" (")[0] for p in row["planets"]]
#         lines.append(f"{', '.join(names)} in {row['sign_name']}")
#     return "\n".join(lines)
