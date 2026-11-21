"""Generate the UAV Concept Lab system architecture diagram.

Outputs:
  diagrams/system_architecture.svg — hand-generated vector diagram (primary)
  diagrams/system_architecture.mmd — Mermaid source for the same diagram

Everything is conceptual and non-operational. All values are simulated/fictional.

Usage:
    python src/generate_diagrams.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = PROJECT_ROOT / "diagrams"

LINE = "#E6F3FF"
ACCENT = "#A8D6F0"
FONT = "Consolas, 'Courier New', monospace"


def xmltext(text: str) -> str:
    """Escape a text value for use inside an SVG text element."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# High-level system blocks (conceptual, non-operational).
BLOCKS = [
    ("Airframe", "conceptual vehicle structure", 0),
    ("Power Management", "power supply (conceptual)", 1),
    ("Computing", "onboard processor (conceptual)", 2),
    ("Sensors", "mission payloads (conceptual)", 3),
    ("Communications", "data link (conceptual)", 4),
    ("Operator Interface", "ground station (conceptual)", 5),
]

# Conceptual relationships between the blocks.
RELATIONSHIPS = [
    ("Airframe", "Power Management", "Power integration"),
    ("Power Management", "Computing", "Provides power"),
    ("Computing", "Sensors", "Processes sensor data"),
    ("Sensors", "Communications", "Data uplink (conceptual)"),
    ("Communications", "Operator Interface", "Uplink (conceptual)"),
]


def svg_doc(width: int, height: int, viewbox: str, body: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="{viewbox}">\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def grid(width: int, height: int, step: int = 20) -> str:
    """Subtle blueprint grid on the background."""
    lines = [f'<rect width="{width}" height="{height}" fill="#0A1E2F"/>']
    for x in range(step, width + 1, step):
        lines.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="#173A52" stroke-width="0.5" opacity="0.35"/>'
        )
    for y in range(step, height + 1, step):
        lines.append(
            f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#173A52" stroke-width="0.5" opacity="0.35"/>'
        )
    return "\n".join(lines)


def caption(text: str, x: int, y: int, size: int = 18, fill: str = LINE) -> str:
    text = xmltext(text)
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" letter-spacing="1" opacity="0.95">{text}</text>'
    )


def block_center_x(index: int) -> int:
    """Center x of block i (boxes laid out in a row)."""
    return 40 + 130 * index + 55


def box(index: int, y: int = 190, height: int = 116) -> str:
    name, subtitle, _ = BLOCKS[index]
    x = 40 + 130 * index
    return (
        f'<rect x="{x}" y="{y}" width="110" height="{height}" rx="8" '
        f'stroke="{LINE}" stroke-width="1.5" fill="#10293D"/>'
        f'<text x="{x + 55}" y="{y + 42}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="15" fill="{LINE}" opacity="0.95">{name}</text>'
        f'<text x="{x + 55}" y="{y + 68}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="11" fill="{ACCENT}" opacity="0.8">{subtitle}</text>'
    )


def arrowhead(px: int, py: int, dir_x: int) -> str:
    size = 8
    if dir_x == 1:
        pts = f"{px},{py} {px - size},{py - size // 2} {px - size},{py + size // 2}"
    else:
        pts = f"{px},{py} {px + size},{py - size // 2} {px + size},{py + size // 2}"
    return f'<polygon points="{pts}" fill="{LINE}" opacity="0.9"/>'


def horizontal_arrow(x1: int, x2: int, y: int, label: str, label_y: int) -> list[str]:
    """Straight arrow between two block centers with a centered label."""
    mid = (x1 + x2) / 2
    body = [
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{LINE}" stroke-width="1.2" opacity="0.9"/>',
        caption(label, mid, label_y, size=11, fill=ACCENT),
    ]
    if x2 > x1:
        body.append(arrowhead(x2, y, 1))
    else:
        body.append(arrowhead(x2, y, -1))
    return body


def loop_arrow(from_idx: int, to_idx: int, y: int = 290, label: str = "") -> list[str]:
    """Vertical-routed arrow from one block back to another (conceptual loop)."""
    fx = 40 + 130 * from_idx
    tx = 40 + 130 * to_idx
    body = [
        f'<path d="M{fx + 110} {y} L{fx + 110} {y + 30} L{tx} {y + 30} L{tx} {y}" '
        f'stroke="{LINE}" stroke-width="1.2" fill="none" opacity="0.85"/>',
        arrowhead(tx, y, -1),
    ]
    if label:
        body.append(caption(label, (fx + tx) / 2 + 55, y - 18, size=11, fill=ACCENT))
    return body


def render() -> str:
    w, h = 900, 560
    body = [
        grid(w, h),
        caption(
            "UAV CONCEPT VISUALIZATION LAB — SYSTEM ARCHITECTURE (CONCEPTUAL, NON-OPERATIONAL)",
            40, 30, size=18,
        ),
        caption(
            "High-level relationships between major system blocks — concept only. "
            "No operational design or implementation specs. Values/labels are simulated/fictional.",
            40, 52, size=13, fill="#7D9FB8",
        ),
    ]
    # Blocks
    for i in range(len(BLOCKS)):
        body.append(box(i))
    # Conceptual relationships (forward arrows between blocks)
    for a, b, label in RELATIONSHIPS:
        idx_a = next(i for i, blk in enumerate(BLOCKS) if blk[0] == a)
        idx_b = next(i for i, blk in enumerate(BLOCKS) if blk[0] == b)
        body.extend(horizontal_arrow(block_center_x(idx_a), block_center_x(idx_b), 248, label, 236))
    # Loop: Operator Interface -> Airframe (conceptual control path)
    body.extend(loop_arrow(5, 0, label="Operator Interface → Airframe (Control path, conceptual)"))
    body.append(
        caption(
            "SIMULATED / FICTIONAL — NOT ENGINEERING DATA. No operational design or implementation specs.",
            40, 525, size=11, fill="#7D9FB8",
        )
    )
    return svg_doc(w, h, f"0 0 {w} {h}", body)


def mermaid_source() -> str:
    relationships = "\n".join(
        f"    {a} --> {b}" for a, b in [(x[0], x[1]) for x in RELATIONSHIPS]
    )
    loop = "    OI -.-> AF"
    return (
        "graph LR\n"
        "    AF[Airframe]\n"
        "    PM[Power Management]\n"
        "    CP[Computing]\n"
        "    SN[Sensors]\n"
        "    CM[Communications]\n"
        "    OI[Operator Interface]\n"
        f"{relationships}\n"
        f"{loop}\n"
        '    classDef concept fill:#10293D,stroke:#A8D6F0,color:#E6F3FF,stroke-width:1.5px;\n'
        "    class AF,PM,CP,SN,CM,OI concept;"
    )


def main() -> None:
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    svg = render()
    mmd = mermaid_source()
    svg_path = DIAGRAMS_DIR / "system_architecture.svg"
    mmd_path = DIAGRAMS_DIR / "system_architecture.mmd"
    svg_path.write_text(svg, encoding="utf-8")
    ET.fromstring(svg)  # self-check: confirm the SVG is well-formed
    mmd_path.write_text(mmd + "\n", encoding="utf-8")
    print(f"wrote {svg_path.relative_to(PROJECT_ROOT)}")
    print(f"wrote {mmd_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
