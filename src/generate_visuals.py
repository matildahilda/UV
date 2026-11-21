"""Generate the UAV Concept Lab visual assets and concept drawings as SVG.

All artwork is original and generated programmatically by this script.

Style (professional aerospace/blueprint look):
  - dark navy blueprint background
  - white and light-blue technical linework
  - subtle grid
  - clean monospaced typography, consistent labeling, minimal clutter

Everything produced here is conceptual. No real engineering results are implied.

Usage:
    python src/generate_visuals.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DRAWINGS_DIR = PROJECT_ROOT / "drawings"

# --- Shared visual style ----------------------------------------------------
BG = "#0A1E2F"      # dark navy blueprint background
GRID = "#173A52"    # subtle grid lines
LINE = "#E6F3FF"    # white / light-blue technical linework
ACCENT = "#A8D6F0"  # secondary light-blue accent

FONT = "Consolas, 'Courier New', monospace"


def xmltext(text: str) -> str:
    """Escape a text value for use inside an SVG text element."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_doc(width: int, height: int, viewbox: str, body: list[str]) -> str:
    """Wrap body fragments in a valid SVG document."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="{viewbox}">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def grid(width: int, height: int, step: int = 40) -> str:
    """Subtle blueprint grid on the background."""
    lines = [f'<rect width="{width}" height="{height}" fill="{BG}"/>']
    for x in range(step, width + 1, step):
        lines.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" '
            f'stroke="{GRID}" stroke-width="0.5" opacity="0.35"/>'
        )
    for y in range(step, height + 1, step):
        lines.append(
            f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="0.5" opacity="0.35"/>'
        )
    return "\n".join(lines)


def caption(
    text: str,
    x: int,
    y: int,
    size: int = 20,
    fill: str = LINE,
    opacity: float = 0.9,
) -> str:
    """Small styled caption/label text."""
    text = xmltext(text)
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" opacity="{opacity}" letter-spacing="1.5">{text}</text>'
    )


def leader(x1: int, y1: int, x2: int, y2: int) -> str:
    """Short subtle leader line used to point labels at sections."""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{LINE}" stroke-width="0.8" opacity="0.7"/>'
    )


# ---------------------------------------------------------------------------
# assets/ — visual assets (illustrations)
# ---------------------------------------------------------------------------


def uav_concept() -> str:
    """General UAV concept illustration (side view, conceptual)."""
    w, h = 900, 600
    return svg_doc(w, h, f"0 0 {w} {h}", [
        grid(w, h),
        caption(
            "GENERAL UAV CONCEPT — SIMULATED ILLUSTRATION (NOT ENGINEERING DATA)",
            60, 38,
        ),
        # Wing (main lifting surface, tapered)
        '<polygon points="310,336 525,336 495,372 380,372" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Fuselage (body / avionics bay)
        '<rect x="412" y="360" width="116" height="30" rx="15" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Nose
        '<rect x="396" y="360" width="16" height="30" rx="8" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Tail vertical stabilizer
        '<rect x="534" y="344" width="12" height="40" rx="6" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Rotors (conceptual)
        '<circle cx="440" cy="306" r="18" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        '<circle cx="502" cy="318" r="18" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        # Mission payload pod
        '<rect x="466" y="372" width="28" height="18" rx="4" stroke="#A8D6F0" stroke-width="1.6" fill="none"/>',
        # Labels
        caption("NOSE", 398, 392),
        caption("ROTOR (CONCEPT)", 432, 292),
        caption("ROTOR (CONCEPT)", 508, 316),
        caption("WING (CONCEPT)", 405, 328),
        caption("FUSELAGE / AVIONICS BAY (CONCEPT)", 412, 402),
        caption("TAIL (CONCEPT)", 538, 354),
        caption("MISSION PAYLOAD (CONCEPT)", 468, 388),
        caption("GENERAL UAV CONCEPT — ASSET 1/5", 60, 578, size=16, fill="#7D9FB8"),
    ])


def uav_silhouette() -> str:
    """Abstract aircraft silhouette — conceptual visualization."""
    w, h = 900, 600
    return svg_doc(w, h, f"0 0 {w} {h}", [
        grid(w, h),
        caption(
            "ABSTRACT AIRCRAFT SILHOUETTE — CONCEPTUAL (NOT TO SCALE)",
            60, 38,
        ),
        # Nose cone (pointed tip)
        '<polygon points="262,396 304,362 316,398" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Fuselage body (elongated capsule)
        '<rect x="300" y="382" width="360" height="26" rx="13" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Wing slivers (front, tapered)
        '<polygon points="296,376 336,354 392,376" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Wing sliver (rear)
        '<polygon points="636,376 690,352 752,376" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Tail fin
        '<polygon points="680,352 698,394 690,428" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Rotor discs (conceptual)
        '<circle cx="352" cy="392" r="22" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        '<circle cx="696" cy="392" r="22" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        caption(
            "ABSTRACT SILHOUETTE — ASSET 2/5 — CONCEPTUAL (NOT TO SCALE)",
            60, 575, size=16, fill="#7D9FB8",
        ),
    ])


def structure_sections() -> str:
    """Labeled conceptual illustration showing general UAV structure sections."""
    w, h = 900, 600
    return svg_doc(w, h, f"0 0 {w} {h}", [
        grid(w, h),
        caption(
            "CONCEPTUAL STRUCTURE SECTIONS — LABELED (NOT TO SCALE)",
            60, 36,
        ),
        # Airframe tube (central fuselage: top edge y=345, bottom edge y=460)
        '<rect x="320" y="345" width="360" height="115" rx="10" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Wing section (main lifting surface, above the tube)
        '<polygon points="495,322 675,322 665,352 495,355" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Wing root section (junction of wing to fuselage)
        '<polygon points="540,340 605,332 612,344 548,352" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Nose section
        '<polygon points="300,352 326,322 330,354 326,382" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Vertical stabilizer / tail
        '<polygon points="672,322 692,352 686,438 662,438" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Landing gear (conceptual): two gear shafts with wheels
        '<rect x="482" y="457" width="18" height="14" rx="4" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        '<rect x="550" y="457" width="18" height="14" rx="4" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        '<circle cx="492" cy="474" r="7" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        '<circle cx="560" cy="474" r="7" stroke="#E6F3FF" stroke-width="2" fill="none"/>',
        # Power / propulsion section (conceptual)
        '<rect x="425" y="446" width="45" height="14" rx="4" stroke="#E6F3FF" stroke-width="2.5" fill="none"/>',
        # Section labels
        caption("NOSE SECTION (CONCEPT)", 300, 378),
        caption("FUSELAGE – AVIIONICS BAY (CONCEPT)", 398, 424),
        caption("WING ROOT SECTION (CONCEPT)", 526, 346),
        caption("WING SECTION (CONCEPT)", 540, 312),
        caption("VERTICAL STABILIZER / TAIL (CONCEPT)", 678, 334),
        caption("POWER / PROPULSION SECTION (CONCEPT)", 430, 468),
        caption("LANDING GEAR (CONCEPTUAL)", 496, 506),
        caption(
            "CONCEPTUAL STRUCTURE — NOT TO SCALE — ASSET 3/5",
            60, 588, size=16, fill="#7D9FB8",
        ),
        # Leader lines pointing labels at their sections
        leader(316, 365, 324, 354),
        leader(408, 414, 362, 405),
        leader(540, 344, 570, 344),
        leader(600, 324, 640, 324),
        leader(682, 330, 682, 352),
        leader(450, 458, 460, 458),
        leader(500, 500, 500, 482),
    ])


# ---------------------------------------------------------------------------
# drawings/ — concept drawings
# ---------------------------------------------------------------------------


def title_block() -> str:
    """Professional engineering title block (revision & drawing information)."""
    w, h = 800, 420
    rows = [
        ("PROJECT TITLE", "UAV Concept Visualization Lab"),
        ("DRAWING TITLE", "CONCEPTUAL UAV — TITLE BLOCK (SIMULATED)"),
        ("DRAWING NUMBER", "UAV-CVL-T-001 (FICTIONAL)"),
        ("SCALE", "1:1 (CONCEPT)"),
        ("DATE (SIMULATED)", "SIMULATED — generated by UAV Concept Lab script"),
        ("DRAWN BY", "UAV Concept Lab (automated)"),
        ("CHECKED BY", "Not yet — concept stage"),
        ("REVISION", "R1 — CONCEPT (SIMULATED)"),
        ("DEPARTMENT", "Engineering Documentation"),
        ("CLIENT / NOTIONAL", "Notional — Educational & Conceptual Use"),
        ("VERSION CONTROL LINK", "https://github.com/Js-Polaris/Students-Poll"),
        ("STATUS", "CONCEPTUAL — NOT AN APPROVED ENGINEERING RESULT"),
    ]
    body = [
        grid(w, h, step=20),
        f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" stroke="{LINE}" stroke-width="1.5" fill="none"/>',
        f'<rect x="8" y="8" width="{w - 16}" height="30" stroke="{LINE}" stroke-width="1.5" fill="none"/>',
        caption(
            "ENGINEERING TITLE BLOCK — REVISION & DRAWING INFORMATION (SIMULATED)",
            40, 30, size=18,
        ),
    ]
    for i, (key, value) in enumerate(rows):
        y = 90 + i * 26
        if y > h - 30:
            break
        body.append(
            f'<text x="56" y="{y + 8}" font-family="{FONT}" font-size="15" '
            f'fill="{LINE}" opacity="0.95">'
            f'<tspan font-weight="bold">{xmltext(key)}:</tspan>  {xmltext(value)}</text>'
        )
    body.append(
        f'<text x="56" y="370" font-family="{FONT}" font-size="12" fill="{ACCENT}">'
        "All numbers and values are simulated/fictional — not real engineering data.</text>"
    )
    body.append(caption("TITLE BLOCK — R1 (SIMULATED)", 56, 398, size=13, fill=ACCENT))
    return svg_doc(w, h, f"0 0 {w} {h}", body)


def mini_uav(x0: int, y0: int, width: int, height: int) -> list[str]:
    """Mini UAV glyph used inside the technical drawing view frames."""
    glyph = [
        # Wing (main lifting surface)
        '<polygon points="{wx1},{wy} {wx2},{wy} {wxp},{wyw} {wxq},{wyw}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
        # Fuselage (capsule)
        '<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{br}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
        # Nose
        '<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="{nr}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
        # Tail
        '<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="{tr}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
        # Payload pod
        '<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="{pr}" stroke="#A8D6F0" stroke-width="1" fill="none"/>',
        # Rotors
        '<circle cx="{rx1}" cy="{ry1}" r="{rr1}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
        '<circle cx="{rx2}" cy="{ry2}" r="{rr2}" stroke="#E6F3FF" stroke-width="1" fill="none"/>',
    ]
    coords = {
        "wx1": f"{x0 + int(0.08 * width):.0f}", "wy": f"{y0 + int(0.10 * height):.0f}",
        "wx2": f"{x0 + int(0.82 * width):.0f}",
        "wxp": f"{x0 + int(0.71 * width):.0f}", "wyw": f"{y0 + int(0.28 * height):.0f}",
        "wxq": f"{x0 + int(0.20 * width):.0f}",
        "bx": f"{x0 + int(0.32 * width):.0f}", "by": f"{y0 + int(0.28 * height):.0f}",
        "bw": f"{int(0.30 * width):.0f}", "bh": f"{int(0.12 * height):.0f}",
        "br": f"{int(0.04 * height):.0f}",
        "nx": f"{x0 + int(0.12 * width):.0f}", "ny": f"{y0 + int(0.42 * height):.0f}",
        "nw": f"{int(0.08 * width):.0f}", "nh": f"{int(0.45 * height):.0f}",
        "nr": "3",
        "tx": f"{x0 + int(0.74 * width):.0f}", "ty": f"{y0 + int(0.42 * height):.0f}",
        "tw": f"{int(0.07 * width):.0f}", "th": f"{int(0.45 * height):.0f}",
        "tr": "3",
        "px": f"{x0 + int(0.48 * width):.0f}", "py": f"{y0 + int(0.62 * height):.0f}",
        "pw": f"{int(0.13 * width):.0f}", "ph": f"{int(0.10 * height):.0f}",
        "pr": "2",
        "rx1": f"{x0 + int(0.46 * width):.0f}", "ry1": f"{y0 + int(0.18 * height):.0f}",
        "rr1": f"{int(0.06 * height):.0f}",
        "rx2": f"{x0 + int(0.58 * width):.0f}", "ry2": f"{y0 + int(0.22 * height):.0f}",
        "rr2": f"{int(0.06 * height):.0f}",
    }
    return [part.format(**coords) for part in glyph]


def technical_drawing_sheet() -> str:
    """Clean technical drawing sheet layout (front/top/side view frames)."""
    w, h = 1200, 820
    views = [
        ("FRONT VIEW", 80, 100, 320, 470),
        ("TOP VIEW", 420, 100, 320, 470),
        ("SIDE VIEW", 760, 100, 320, 470),
    ]
    body = [
        grid(w, h),
        f'<rect x="10" y="10" width="{w - 20}" height="{h - 20}" stroke="{LINE}" stroke-width="2" fill="none"/>',
        caption(
            "UAV CONCEPT VISUALIZATION LAB — TECHNICAL DRAWING SHEET",
            60, 40, size=20,
        ),
        caption(
            "CONCEPTUAL UAV DRAWING — SIMULATED ILLUSTRATION (NOT ENGINEERING DATA)",
            60, 62, size=13, fill="#7D9FB8",
        ),
    ]
    for name, fx, fy, fw, fh in views:
        body.append(caption(name, fx + 10, fy - 14, size=14))
        body.append(
            f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" '
            f'stroke="{LINE}" stroke-width="1.5" fill="#10293D"/>'
        )
        body.extend(mini_uav(fx + 8, fy + 20, fw - 16, fh - 30))
    # Revision history table
    body.append(caption("REVISION HISTORY (SIMULATED)", 80, 590, size=16))
    body.append(
        f'<rect x="80" y="615" width="520" height="80" rx="4" stroke="{LINE}" stroke-width="1.5" fill="none"/>'
    )
    revs = [
        ("REV", "DATE", "DESCRIPTION", "STATUS", False),
        ("R1", "SIMULATED 2026-11-21", "Concept drawing sheet created", "CONCEPT", True),
        ("R0", "—", "Initial concept", "CONCEPT", False),
    ]
    for i, (r, d, desc, status, bold) in enumerate(revs):
        y = 645 + i * 22
        cols = [(r, 100), (d, 240), (desc, 420), (status, 790)]
        for text, x in cols:
            weight = ' font-weight="bold"' if bold else ""
            body.append(
                f'<text x="{x}" y="{y + 12}" font-family="{FONT}" font-size="13" '
                f'fill="{LINE}" opacity="0.95"{weight}>{text}</text>'
            )
    # Notes
    body.append(caption("NOTES (CONCEPTUAL)", 80, 712, size=16))
    notes = [
        "Illustration-only drawing — no manufacturing geometry or approvals.",
        "All linework, dimensions, values and numbers are simulated/fictional.",
        "This sheet does not constitute engineering data or a design approval.",
        "Concept study for visualization, education and documentation purposes.",
        "Related deliverables: assets/ (concept illustrations), diagrams/ (system architecture).",
    ]
    for i, note in enumerate(notes):
        body.append(
            caption("– " + note if i else note, 80, 736 + i * 18, size=12, fill="#7D9FB8")
        )
    body.append(
        caption(
            "DRAWING NUMBER: UAV-CVL-D-001 — SCALE: 1:1 (CONCEPT) — SHEET 1 OF 1 — "
            "GENERATED BY: UAV CONCEPT LAB — ALL SIMULATED",
            60, 800, size=12, fill=ACCENT,
        )
    )
    return svg_doc(w, h, f"0 0 {w} {h}", body)


# ---------------------------------------------------------------------------
# Generator entry point
# ---------------------------------------------------------------------------


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    DRAWINGS_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "assets/uav_concept.svg": uav_concept(),
        "assets/uav_silhouette.svg": uav_silhouette(),
        "assets/structure_sections.svg": structure_sections(),
        "drawings/title_block.svg": title_block(),
        "drawings/technical_drawing_sheet.svg": technical_drawing_sheet(),
    }
    for rel, content in files.items():
        path = PROJECT_ROOT / rel
        path.write_text(content, encoding="utf-8")
        ET.fromstring(content)  # self-check: confirm the SVG is well-formed
        print(f"wrote {rel}")
    print(f"done — {len(files)} files generated under {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
