from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
from app.constants import SIGN_NAMES

def _extract_text_nodes(svg_text: str) -> List[Dict]:
    safe = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
    root = ET.fromstring(safe)
    out: List[Dict] = []
    for t in root.findall(".//{http://www.w3.org/2000/svg}text"):
        x, y = t.get("x"), t.get("y")
        if not x or not y:
            continue
        s = "".join(t.itertext()).strip()
        if not s:
            continue
        try:
            xf, yf = float(x), float(y)
        except ValueError:
            continue
        out.append({"x": xf, "y": yf, "text": s})
    return out

def _grid_from_lines(svg_text: str) -> Tuple[list[float], list[float]]:
    safe = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", svg_text)
    root = ET.fromstring(safe)
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

def parse_sav_totals_from_svg(svg_bytes: bytes) -> List[Dict]:
    """
    Return 12 rows:
      [{"no": 1, "sign_name": "Aries", "total": 25}, ...]
    Heuristics:
      - Each sign cell is labeled with 1..12 somewhere inside it (we ignore this label).
      - Small integers (0..8 or so) within the same cell are contributions; summed per cell.
      - If the SVG already prints a 'Total' in the cell, we try to detect numbers > 8 and prefer that as total.
    """
    svg_text = svg_bytes.decode("utf-8")
    xs, ys = _grid_from_lines(svg_text)
    texts = _extract_text_nodes(svg_text)

    # 1) map cell -> sign number using 1..12 label
    cell_to_no: Dict[tuple[int,int], int] = {}
    for n in texts:
        if n["text"].isdigit():
            v = int(n["text"])
            if 1 <= v <= 12:
                k = _cell_index(n["x"], n["y"], xs, ys)
                if k:
                    # take the first digit we encounter per cell as the house label
                    cell_to_no.setdefault(k, v)

    # 2) collect other numeric tokens per cell
    per_cell_values: Dict[tuple[int,int], List[int]] = {}
    for n in texts:
        s = n["text"]
        # numeric token?
        if not re.fullmatch(r"-?\d+", s):
            continue
        num = int(s)

        k = _cell_index(n["x"], n["y"], xs, ys)
        if not k:
            continue

        # if this numeric equals the 1..12 label for this cell, ignore
        if k in cell_to_no and cell_to_no[k] == num and (1 <= num <= 12):
            continue

        per_cell_values.setdefault(k, []).append(num)

    # 3) compute sign totals per mapped cell
    no_to_total: Dict[int, int] = {i: 0 for i in range(1, 13)}

    for cell, vals in per_cell_values.items():
        no = cell_to_no.get(cell)
        if not no:
            continue
        if not vals:
            continue

        # Heuristic: if any value > 8 exists, it's probably an already-rendered total -> take max
        # otherwise sum small contribution digits
        maxi = max(vals)
        if maxi > 8:
            total = maxi
        else:
            total = sum(v for v in vals if 0 <= v <= 8)

        no_to_total[no] = max(no_to_total[no], total)

    # 4) build ordered rows
    rows: List[Dict] = []
    for no in range(1, 13):
        rows.append({
            "no": no,
            "sign_name": SIGN_NAMES.get(no, f"Sign {no}"),
            "total": int(no_to_total.get(no, 0)),
        })
    return rows

def simple_sav_lines(rows: List[Dict]) -> List[str]:
    """
    Returns: ["ASHTAKAVARGA TOTALS", "Aries: 25", ..., "Grand Total: 322"]
    """
    out = ["ASHTAKAVARGA TOTALS"]
    g = 0
    for r in rows:
        out.append(f"{r['sign_name']}: {r['total']}")
        g += r["total"]
    out.append(f"Grand Total: {g}")
    return out
