"""Generate conceptual UAV 3D models as ASCII STL files.

Outputs:
  models/uav_concept.stl — conceptual UAV (airframe tube, nose cone, wing,
                           vertical tail fin, two rotor discs).

Conceptual visualization model only — no manufacturing geometry is implied.
Units are meters (model scale).

Usage:
    python src/generate_3d_models.py
"""

from __future__ import annotations

import math
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_norm(v):
    m = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if m == 0:
        return None
    return (v[0] / m, v[1] / m, v[2] / m)


def _basis(axis):
    """Orthonormal basis (u, v) perpendicular to axis."""
    ax = vec_norm(axis)
    ref = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.95 else (1.0, 0.0, 0.0)
    u = vec_norm(vec_cross(ax, ref))
    v = vec_norm(vec_cross(ax, u))
    return ax, u, v


def _ring(center, u, v, radius, segments):
    """Circle of points in the plane spanned by u and v, around center."""
    pts = []
    for k in range(segments):
        ang = 2 * math.pi * k / segments
        pts.append(
            (
                center[0] + u[0] * radius * math.cos(ang) + v[0] * radius * math.sin(ang),
                center[1] + u[1] * radius * math.cos(ang) + v[1] * radius * math.sin(ang),
                center[2] + u[2] * radius * math.cos(ang) + v[2] * radius * math.sin(ang),
            )
        )
    return pts


def cylinder(p0, p1, radius, segments=24):
    """Triangles for a cylinder along p0 -> p1 (flat end caps)."""
    tris = []
    axis = vec_sub(p1, p0)
    ax, u, v = _basis(axis)
    ring0 = _ring(p0, u, v, radius, segments)
    ring1 = _ring(p1, u, v, radius, segments)
    # End caps (fans from the axis endpoints).
    for cap, ring_pts in ((p0, ring0), (p1, ring1)):
        for k in range(1, segments - 1):
            tris.append((cap, ring_pts[k], ring_pts[k + 1]))
    # Lateral surface.
    for k in range(segments):
        k2 = (k + 1) % segments
        tris.append((ring0[k], ring0[k2], ring1[k2]))
        tris.append((ring0[k], ring1[k2], ring1[k]))
    return tris


def cone(apex, base_center, base_radius, segments=24):
    """Triangles for a cone with base at base_center and apex at apex."""
    tris = []
    axis = vec_sub(apex, base_center)
    ax, u, v = _basis(axis)
    ring = _ring(base_center, u, v, base_radius, segments)
    for k in range(1, segments - 1):
        tris.append((base_center, ring[k], ring[k + 1]))
    for k in range(segments):
        k2 = (k + 1) % segments
        tris.append((apex, ring[k], ring[k2]))
    return tris


def box(center, sx, sy, sz):
    """Triangles for an axis-aligned box with the given center and sizes."""
    x, y, z = center
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    xs = [x - hx, x + hx]
    ys = [y - hy, y + hy]
    zs = [z - hz, z + hz]
    corners = [(xv, yv, zv) for xv in xs for yv in ys for zv in zs]
    tris = []

    def face(a, b, c, d):
        tris.append((corners[a], corners[b], corners[c]))
        tris.append((corners[a], corners[c], corners[d]))

    # Corner index = i_x * 4 + i_y * 2 + i_z
    face(0, 2, 3, 1)  # x = xs[0]
    face(4, 6, 7, 5)  # x = xs[1]
    face(0, 4, 5, 1)  # y = ys[0]
    face(2, 6, 7, 3)  # y = ys[1]
    face(0, 4, 6, 2)  # z = zs[0]
    face(1, 5, 7, 3)  # z = zs[1]
    return tris


def write_stl(path, tris, name="uav_concept"):
    """Write an ASCII STL file; returns the number of facets written."""
    lines = [f"solid {name}"]
    written = 0
    for v0, v1, v2 in tris:
        n = vec_norm(vec_cross(vec_sub(v1, v0), vec_sub(v2, v0)))
        if n is None:
            continue
        lines.append(f"facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")
        lines.append("  outer loop")
        for v in (v0, v1, v2):
            lines.append(f"    vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
        lines.append("  endloop")
        lines.append("endfacet")
        written += 1
    lines.append(f"endsolid {name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return written


def validate_stl(path, expected_facets, expected_bbox, tolerance=0.05):
    """Re-read the STL and check facet/vertex counts and the bounding box."""
    text = path.read_text(encoding="utf-8")
    facets = text.count("facet normal")
    vertices = text.count("    vertex ")
    if facets != expected_facets:
        raise SystemExit(f"ERROR: {path}: facet count {facets} != expected {expected_facets}")
    if vertices != 3 * expected_facets:
        raise SystemExit(f"ERROR: {path}: vertex count {vertices} != {3 * expected_facets}")
    xs, ys, zs = [], [], []
    for m in re.finditer(r"vertex ([-\d.]+) ([-\d.]+) ([-\d.]+)", text):
        xs.append(float(m.group(1)))
        ys.append(float(m.group(2)))
        zs.append(float(m.group(3)))
    bbox = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
    if not all(math.isclose(a, b, abs_tol=tolerance) for a, b in zip(bbox, expected_bbox)):
        raise SystemExit(f"ERROR: {path}: bbox {bbox} != expected {expected_bbox}")
    print(
        f"validated {path}: {facets} facets; "
        f"bbox x[{bbox[0]:.3f},{bbox[1]:.3f}] y[{bbox[2]:.3f},{bbox[3]:.3f}] z[{bbox[4]:.3f},{bbox[5]:.3f}]"
    )


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    tris = []
    # Airframe tube (central fuselage), horizontal along X.
    tris += cylinder((-0.95, 0.0, 0.0), (0.25, 0.0, 0.0), 0.075)
    # Nose cone on the front of the tube.
    tris += cone((-1.05, 0.0, 0.0), (-0.95, 0.0, 0.0), 0.055)
    # Wing (horizontal lifting surface).
    tris += box((0.0, 0.45, 0.0), 1.30, 0.30, 0.02)
    # Vertical tail fin (rear, above the tube).
    tris += box((0.45, 0.0, 0.14), 0.05, 0.40, 0.28)
    # Two rotor discs (vertical rectangles in the XZ plane).
    tris += box((-0.45, 0.5, 0.08), 0.08, 0.012, 0.28)
    tris += box((0.0, 0.5, 0.08), 0.08, 0.012, 0.28)

    path = MODELS_DIR / "uav_concept.stl"
    facets = write_stl(path, tris)
    expected_facets = 186
    if facets != expected_facets:
        raise SystemExit(f"ERROR: wrote {facets} facets, expected {expected_facets}")
    expected_bbox = (-1.05, 0.65, -0.2, 0.6, -0.075, 0.28)
    validate_stl(path, expected_facets, expected_bbox)
    print(f"wrote {path} — {facets} triangles")


if __name__ == "__main__":
    main()
