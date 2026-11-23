"""Generate UAV Concept Lab schematic designs as SVG.

Outputs:
  schematics/avionics_schematic.svg        — avionics / system block schematic
  schematics/mission_profile_schematic.svg — mission profile schematic (simulated)
  schematics/wiring_schematic.svg         — wiring diagram (UAV concept)
  schematics/pcb_schematic.svg            — custom PCB circuit schematic

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


def _label_at(mx: float, my: float, label: str, font_size: int, perp: tuple[float, float], label_offset: int):
    perp_x, perp_y = perp
    if perp_y > 0:
        perp_x, perp_y = -perp_x, -perp_y
    return (
        f'<text x="{mx + perp_x * label_offset:.0f}" y="{my + perp_y * label_offset:.0f}" '
        f'text-anchor="middle" font-family="{FONT}" font-size="{font_size}" '
        f'fill="{ACCENT}" opacity="0.9">{xmltext(label)}</text>'
    )


def arrow(ax: int, ay: int, bx: int, by: int, label: str, font_size: int = 10, label_offset: int = 8) -> list[str]:
    """Arrow from point A to point B with a centered label near the line."""
    length = math.hypot(bx - ax, by - ay)
    if length == 0:
        return []
    ux, uy = (bx - ax) / length, (by - ay) / length
    out = [
        f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{LINE}" stroke-width="1.2" opacity="0.9"/>',
        arrowhead(bx, by, ux, uy),
    ]
    if label:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        out.append(_label_at(mx, my, label, font_size, (-uy, ux), label_offset))
    return out


def wire(ax: int, ay: int, bx: int, by: int, label: str, font_size: int = 10, label_offset: int = 8) -> list[str]:
    """Wiring line between two terminals: line + connection dots + wire label."""
    out = [
        f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{LINE}" stroke-width="1" opacity="0.9"/>',
        f'<circle cx="{ax}" cy="{ay}" r="3" fill="{LINE}" opacity="0.8"/>',
        f'<circle cx="{bx}" cy="{by}" r="3" fill="{LINE}" opacity="0.8"/>',
    ]
    if label:
        length = math.hypot(bx - ax, by - ay)
        if length == 0:
            return out
        ux, uy = (bx - ax) / length, (by - ay) / length
        mx, my = (ax + bx) / 2, (ay + by) / 2
        out.append(_label_at(mx, my, label, font_size, (-uy, ux), label_offset))
    return out


def block(x: int, y: int, w: int, h: int, label: str, subtitle: str = "") -> list[str]:
    """Styled block used in the avionics schematic (label fits inside the block)."""
    label = xmltext(label)
    subtitle = xmltext(subtitle)
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" stroke="{LINE}" stroke-width="1.5" fill="#10293D"/>',
        f'<text x="{x + w / 2}" y="{y + h / 2 - 4}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{LINE}" opacity="0.95">{label}</text>',
    ]
    if subtitle:
        out.append(
            f'<text x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{ACCENT}" opacity="0.9">{subtitle}</text>'
        )
    return out


def footprint(cx: int, cy: int, w: int, h: int, label: str, terminals: int = 0) -> list[str]:
    """Simplified component footprint (silkscreen outline + label + terminal dots)."""
    out = [
        f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="{min(4, h / 2)}" stroke="{LINE}" stroke-width="1.2" fill="none"/>',
        f'<text x="{cx}" y="{cy}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{ACCENT}">{xmltext(label)}</text>',
    ]
    if terminals:
        for k in range(terminals):
            y = cy - h / 2 + (k + 0.5) * h / terminals
            out.append(f'<circle cx="{cx - w / 2}" cy="{y:.1f}" r="2" fill="{LINE}" opacity="0.9"/>')
    return out


def trace(x1: int, y1: int, x2: int, y2: int, label: str = "", width: int = 2) -> list[str]:
    """Copper trace between two endpoints with terminal dots and a wire label."""
    out = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="{width}" opacity="0.9"/>',
        f'<circle cx="{x1}" cy="{y1}" r="3" fill="{LINE}" opacity="0.8"/>',
        f'<circle cx="{x2}" cy="{y2}" r="3" fill="{LINE}" opacity="0.8"/>',
    ]
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out.append(
            f'<text x="{mx:.0f}" y="{my - 4:.0f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="10" fill="{ACCENT}" opacity="0.9">{xmltext(label)}</text>'
        )
    return out


def avionics_schematic() -> str:
    """Avionics / system block schematic (conceptual relationships).

    Two rows of four blocks. Row 1: Battery, Power Dist/BMS, Flight Controller,
    Actuators. Row 2: Sensor Bay, Telemetry Bus, GPS/GNSS Nav, Airframe.
    All labels fit inside their blocks.
    """
    w, h = 1100, 570
    blocks = [
        # Row 1 (top): power & control blocks.
        ("Battery (Conceptual)", "12.6 V — conceptual"),
        ("Power Dist / BMS (Concept)", "smart distribution"),
        ("Flight Controller (Concept)", "nav & control logic"),
        ("Actuators (Concept)", "motors, ESCs, servos — conceptual"),
        # Row 2 (bottom): sensors, uplink, GPS, airframe.
        ("Sensor Bay (Concept)", "observation sensors"),
        ("Telemetry Data Bus (Concept)", "status uplink"),
        ("GPS / GNSS Nav (Concept)", "position fix"),
        ("Airframe", "conceptual structure"),
    ]
    x0, bw, bh = 46, 220, 80
    col_step = 260  # bw + gap between adjacent blocks
    row1_y, row2_y = 150, 310
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
    body.extend(arrow(cx(0), 190, cx(1), 190, "provides power", label_offset=50))
    body.extend(arrow(cx(1), 190, cx(2), 190, "powers avionics", label_offset=50))
    body.extend(arrow(cx(2), 190, cx(3), 190, "control commands", label_offset=50))
    body.extend(arrow(cx(2), 190, cx(0), 350, "data + power"))
    body.extend(arrow(cx(2), 190, cx(1), 350, "publishes status"))
    body.extend(arrow(cx(2), 190, cx(2), 350, "navigation data"))
    body.extend(arrow(cx(3), 190, cx(3), 350, "attached to airframe"))
    body.extend(arrow(cx(0), 350, cx(3), 350, "mounted on airframe", label_offset=50))
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


def wiring_schematic() -> str:
    """Wiring diagram for the UAV concept (schematic-level connection view).

    Row 1 (top): Battery, Power Dist/BMS, Flight Controller, Actuators.
    Row 2 (bottom): Sensor Bay, Telemetry Bus, GPS/GNSS Nav, Airframe.
    Labeled wires connect the components conceptually.
    """
    w, h = 1100, 570
    blocks = [
        # Row 1 (top): power & control blocks.
        ("Battery (Conceptual)", "12.6 V — conceptual"),
        ("Power Dist / BMS (Concept)", "smart distribution"),
        ("Flight Controller (Concept)", "nav & control logic"),
        ("Actuators (Concept)", "motors, ESCs, servos — conceptual"),
        # Row 2 (bottom): sensors, uplink, GPS, airframe.
        ("Sensor Bay (Concept)", "observation sensors"),
        ("Telemetry Data Bus (Concept)", "status uplink"),
        ("GPS / GNSS Nav (Concept)", "position fix"),
        ("Airframe", "conceptual structure"),
    ]
    x0, bw, bh = 46, 220, 80
    col_step = 260
    row1_y, row2_y = 150, 310
    cx = lambda col: x0 + col * col_step + bw / 2

    body = [
        grid(w, h),
        caption(
            "UAV CONCEPT VISUALIZATION LAB — WIRING DIAGRAM (SIMULATED, CONCEPTUAL)",
            30, 34, size=18,
        ),
        caption(
            "UAV concept wiring diagram — schematic-level connection view",
            30, 54, size=12, fill="#7D9FB8",
        ),
    ]
    for col, (label, subtitle) in enumerate(blocks):
        row_y = row1_y if col < 4 else row2_y
        body.extend(block(x0 + (col % 4) * col_step, row_y, bw, bh, label, subtitle))
    # Labeled conceptual wiring connections.
    body.extend(wire(cx(0), 190, cx(1), 190, "BAT+"))
    body.extend(wire(cx(1), 190, cx(2), 190, "+V logic"))
    body.extend(wire(cx(2), 190, cx(3), 190, "control signals A/B", label_offset=52))
    body.extend(wire(cx(2), 190, cx(0), 350, "sensor power/data"))
    body.extend(wire(cx(2), 190, cx(1), 350, "telemetry output"))
    body.extend(wire(cx(2), 190, cx(2), 350, "GPS data"))
    body.extend(wire(cx(0), 350, cx(3), 350, "sensor mount", label_offset=50))
    body.extend(wire(cx(3), 190, cx(3), 350, "actuator mount"))
    body.append(caption("All connections are conceptual/simulated — not real wiring specs.", 30, 548, size=11, fill="#7D9FB8"))
    body.append(caption("SIMULATED / FICTIONAL — NOT REAL WIRING DIAGRAM (conceptual)", 30, 566, size=11, fill="#7D9FB8"))
    return svg_doc(w, h, f"0 0 {w} {h}", body)


def pcb_schematic() -> str:
    """Custom PCB circuit schematic — board outline, copper traces, footprints, drill holes.

    Schematic level only; not a manufacturable board design.
    """
    w, h = 1280, 800
    body = [
        grid(w, h),
        caption(
            "UAV CONCEPT VISUALIZATION LAB — CUSTOM PCB CIRCUIT SCHEMATIC (SIMULATED, CONCEPTUAL)",
            30, 34, size=18,
        ),
        caption(
            "Custom board schematic — board outline, copper traces, footprints, drill holes",
            30, 54, size=12, fill="#7D9FB8",
        ),
        # Board outline (the "board" interior area).
        f'<rect x="20" y="20" width="940" height="640" rx="8" stroke="{LINE}" stroke-width="1.5" fill="#0A1E2F"/>',
    ]
    # Component footprints (silkscreen outlines + labels + terminal dots).
    body.extend(footprint(80, 230, 10, 16, "BAT", terminals=2))
    body.extend(footprint(240, 230, 16, 18, "PD"))
    body.extend(footprint(400, 230, 22, 18, "FC"))
    body.extend(footprint(620, 230, 16, 10, "TB"))
    body.extend(footprint(200, 430, 16, 12, "SB"))
    body.extend(footprint(400, 430, 10, 8, "GPS"))
    body.extend(footprint(560, 430, 12, 22, "ESC", terminals=3))
    body.extend(footprint(800, 430, 36, 28, "Airframe"))
    # Copper traces connecting footprints.
    body.extend(trace(80, 230, 240, 230, "BAT+"))
    body.extend(trace(240, 230, 400, 230, "PD → FC"))
    body.extend(trace(400, 230, 620, 230, "FC → TB"))
    body.extend(trace(400, 230, 400, 430, "FC → GPS"))
    body.extend(trace(400, 230, 560, 430, "FC → ESC"))
    body.extend(trace(560, 430, 800, 430, "ESC → Airframe"))
    # Drill holes on the board.
    for hx, hy in ((100, 500), (300, 500), (700, 500), (930, 480)):
        body.append(f'<circle cx="{hx}" cy="{hy}" r="3" stroke="{LINE}" stroke-width="1" fill="none"/>')
    body.append(
        caption("SIMULATED / FICTIONAL — NOT A MANUFACTURABLE PCB DESIGN (conceptual)", 30, 772, size=11, fill="#7D9FB8")
    )
    body.append(
        caption("Drawn-out board: board outline, copper traces, simplified footprints, drill holes.", 30, 792, size=11, fill="#7D9FB8")
    )
    return svg_doc(w, h, f"0 0 {w} {h}", body)


FILES = {
    "schematics/avionics_schematic.svg": avionics_schematic,
    "schematics/mission_profile_schematic.svg": mission_profile_schematic,
    "schematics/wiring_schematic.svg": wiring_schematic,
    "schematics/pcb_schematic.svg": pcb_schematic,
}


def main() -> None:
    SCHEMATICS_DIR.mkdir(parents=True, exist_ok=True)
    for rel, builder in FILES.items():
        content = builder()
        path = PROJECT_ROOT / rel
        path.write_text(content, encoding="utf-8")
        ET.fromstring(content)  # self-check: confirm the SVG is well-formed
        print(f"wrote {rel}")
    print(f"done — {len(FILES)} schematic files generated under {PROJECT_ROOT}")


if __name__ == "__main__":
    main()
