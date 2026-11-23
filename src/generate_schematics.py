"""Generate UAV Concept Lab schematic designs as SVG.

Outputs:
  schematics/avionics_schematic.svg        — avionics / system block schematic
  schematics/mission_profile_schematic.svg — mission profile schematic (simulated)

Usage:
    python src/generate_schematics.py
"""

from __future__ import annotations

import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_visuals import ACCENT, FONT, LINE, caption, grid, svg_doc, xmltext

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMATICS_DIR = PROJECT_ROOT / "schematics"


def arrowhead(px: int, py: int, ux: float, uy: float, size: int = 8) -> str:
    """Triangle head of an arrow pointing along (ux, uy) with its tip at (px, py)."""
    perp_x, perp_y = -uy, ux
    b1x = px - ux * size + perp_x * size / 2
    b1y = py - uy * size + perp_y * size / 2
    b2x = px - ux * size - perp_x * size / 2
    b2y = py - uy * size - perp_y * size / 2
    return f'<polygon points="{px},{py} {b1x:.0f},{b1y:.0f} {b2x:.0f},{b2y:.0f}" fill="{LINE}" opacity="0.9"/>'


def arrow(ax: int, ay: int, bx: int, by: int, label: str, font_size: int = 11) -> list[str]:
    """Arrow from point A to point B with a centered label near the midpoint.

    Handles horizontal, vertical and diagonal connections.
    """
    length = math.hypot(bx - ax, by - ay)
    if length == 0:
        return []
    ux, uy = (bx - ax) / length, (by - ay) / length
    out = [
        f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{LINE}" stroke-width="1.2" opacity="0.9"/>',
        arrowhead(bx, by, ux, uy),
        f'<text x="{(ax + bx) / 2:.0f}" y="{(ay + by) / 2 - 4:.0f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="{font_size}" fill="{ACCENT}" opacity="0.9">{xmltext(label)}</text>',
    ]
    return out


def block(x: int, y: int, w: int, h: int, label: str, subtitle: str = "") -> list[str]:
    """Styled block used in the avionics schematic (label fits inside the block)."""
    label = xmltext(label)
    subtitle = xmltext(subtitle)
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" stroke="{LINE}" stroke-width="1.5" fill="#10293D"/>',
        f'<text x="{x + w / 2}" y="{y + h / 2 - 4}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{LINE}" opacity="0.95">{label}</text>',
    ]
    if subtitle:
        out.append(
            f'<text x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{ACCENT}" opacity="0.9">{subtitle}</text>'
        )
    return out


def avionics_schematic() -> str:
    """Avionics / system block schematic (conceptual relationships).

    Two rows of four blocks. All labels are short enough to fit inside their
    blocks (240 px wide); connectors are drawn between the rows.
    """
    w, h = 1100, 570
    blocks = [
        # Row 1 (top): core power & control blocks.
        ("Battery (Conceptual)", "12.6 V — conceptual"),
        ("Power Dist / BMS (Concept)", "smart distribution"),
        ("Flight Controller (Concept)", "nav & control logic"),
        ("GPS / GNSS Nav (Concept)", "position fix"),
        # Row 2 (bottom): sensors, uplink, actuators, airframe.
        ("Sensor Bay (Concept)", "observation sensors"),
        ("Telemetry Data Bus (Concept)", "status uplink"),
        ("Actuators (Concept)", "motors, ESCs, servos — conceptual"),
        ("Airframe", "conceptual structure"),
    ]
    x0 = 46
    bw, bh = 240, 80
    col_step = 256  # bw (240) + 16 px spacing
    row1_y, row2_y = 160, 300
    cx = lambda col: x0 + col * col_step + bw / 2

    body = [
        grid(w, h),
        caption(
            "UAV CONCEPT VISUALIZATION LAB — AVIONICS / SYSTEM SCHEMATIC (SIMULATED, CONCEPTUAL)",
            30, 34, size=18,
        ),
        caption(
            "High-level avionics block schematic — conceptual, non-operational",
            30, 54, size=12, fill="#7D9FB8",
        ),
    ]
    for col, (label, subtitle) in enumerate(blocks):
        row_y = row1_y if col < 4 else row2_y
        body.extend(block(x0 + (col % 4) * col_step, row_y, bw, bh, label, subtitle))
    # Conceptual relationships between blocks.
    body.extend(arrow(cx(0), 245, cx(1), 245, "provides power"))
    body.extend(arrow(cx(1), 245, cx(2), 245, "powers avionics"))
    body.extend(arrow(cx(2), 245, cx(3), 245, "sends commands"))
    body.extend(arrow(cx(2), 200, cx(0), 340, "data + power"))         # FC -> Sensor Bay
    body.extend(arrow(cx(2), 200, cx(1), 340, "publishes status"))      # FC -> Telemetry Bus
    body.extend(arrow(cx(2), 200, cx(2), 340, "control commands"))      # FC -> Actuators
    body.extend(arrow(cx(0), 290, cx(3), 290, "mounted on airframe"))   # Sensor Bay -> Airframe
    body.extend(arrow(cx(2), 290, cx(3), 290, "attached to airframe"))  # Actuators -> Airframe
    body.append(
        caption("All blocks are conceptual/simulated — not real avionics specs.", 30, 548, size=11, fill="#7D9FB8")
    )
    body.append(
        caption("SIMULATED / FICTIONAL — NOT REAL AVIONICS DATA (conceptual)", 30, 566, size=11, fill="#7D9FB8")
    )
    return svg_doc(w, h, f"0 0 {w} {h}", body)


def mission_profile_schematic() -> str:
    """Conceptual time–altitude mission profile (SIMULATED values)."""
    w, h = 900, 600
    x0, x1, y_top, y_ground = 60, 780, 140, 460
    scale_x = (x1 - x0) / 10.0           # 72 px per time unit
    scale_y = (y_ground - y_top) / 160.0  # 2 px per altitude unit

    def pt(t, alt):
        return (x0 + t * scale_x, y_ground - alt * scale_y)

    # Simulated mission profile: takeoff, climb, cruise, loiter, approach, landing.
    profile = [
        (0.0, 0.0),
        (0.5, 0.0),
        (2.0, 60.0),
        (4.0, 160.0),
        (6.0, 160.0),
        (8.0, 160.0),
        (9.0, 60.0),
        (9.5, 0.0),
        (10.0, 0.0),
    ]
    points = [pt(t, alt) for t, alt in profile]
    pts_str = " ".join(f"{x:.0f},{y:.0f}" for x, y in points)
    body = [
        grid(w, h),
        caption(
            "UAV CONCEPT VISUALIZATION LAB — MISSION PROFILE SCHEMATIC (SIMULATED, CONCEPTUAL)",
            30, 40, size=18,
        ),
        caption(
            "Conceptual time–altitude profile — values are SIMULATED/fictional",
            30, 62, size=12, fill="#7D9FB8",
        ),
        # Axes (altitude 0 at the ground line; time across the plot).
        f'<line x1="{x0}" y1="{y_ground}" x2="{x1}" y2="{y_ground}" stroke="{LINE}" stroke-width="1"/>',
        f'<line x1="{x0}" y1="{y_top}" x2="{x0}" y2="{y_ground}" stroke="{LINE}" stroke-width="1"/>',
        caption("Time (SIMULATED — Conceptual, arbitrary units)", 420, 582, size=12, fill="#7D9FB8"),
        caption("Altitude (SIMULATED — Conceptual, arbitrary units)", 26, 286, size=12, fill="#7D9FB8"),
        # Simulated profile polyline.
        f'<polyline points="{pts_str}" stroke="{LINE}" stroke-width="2" fill="none"/>',
    ]
    labels = [
        ("TAKEOFF (SIM)", 70, 452),
        ("CLIMB (SIM)", 150, 322),
        ("CRUISE (SIM)", 420, 124),
        ("LOITER (SIM)", 555, 124),
        ("APPROACH (SIM)", 690, 322),
        ("LANDING (SIM)", 760, 452),
    ]
    for text, x, y in labels:
        body.append(caption(text, x, y, size=10, fill=ACCENT))
    body.append(
        caption("SIMULATED / FICTIONAL — NOT REAL MISSION DATA (conceptual)", 30, 572, size=11, fill="#7D9FB8")
    )
    return svg_doc(w, h, f"0 0 {w} {h}", body)


def main() -> None:
    SCHEMATICS_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "schematics/avionics_schematic.svg": avionics_schematic(),
        "schematics/mission_profile_schematic.svg": mission_profile_schematic(),
    }
    for rel, content in files.items():
        path = PROJECT_ROOT / rel
        path.write_text(content, encoding="utf-8")
        ET.fromstring(content)  # self-check: confirm the SVG is well-formed
        print(f"wrote {rel}")
    print(f"done — {len(files)} schematic files generated under {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
