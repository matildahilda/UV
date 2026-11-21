"""Simulated telemetry data source for the UAV Concept Lab.

Generates *simulated/fictional* telemetry values for visualization and
dashboard development only. It does **not** connect to any real aircraft,
sensor or control hardware, and it does **not** produce real engineering
results. Every value is marked SIMULATED.

Functions:
    simulated_telemetry(...) -> dict          # one simulated status record
    write_telemetry_file(...) -> Path         # write telemetry_sim.json samples

Usage:
    python simulation/data_source.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SIMULATED = "SIMULATED"
DEFAULT_AIRCRAFT_ID = "SIM-01 (fictional)"


def _simulated_wobble(seed_value: float, base: float, amplitude: float) -> float:
    """Tiny deterministic pseudo-random wobble (visual demo, not real data)."""
    x = (seed_value * 9301.0 + 49297.0) % 233280.0
    return base + amplitude * ((x / 233280.0) * 2.0 - 1.0)


def simulated_telemetry(
    aircraft_id: str = DEFAULT_AIRCRAFT_ID,
    timestamp: str | None = None,
    phase_s: float = 0.0,
) -> dict:
    """Return a dictionary of simulated telemetry values (all SIMULATED)."""
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    return {
        "aircraft_id": aircraft_id,
        "status": f"{SIMULATED} — IDLE",
        "timestamp_utc": ts,
        "mission_id": "M-07 (fictional)",
        "mode": "CONCEPTUAL LOFT PROFILE (SIMULATED)",
        "altitude_m": round(_simulated_wobble(phase_s, 30.0, 10.0), 1),
        "ground_speed_m_s": round(_simulated_wobble(phase_s + 1, 5.0, 9.0), 1),
        "battery_pct": round(max(5.0, _simulated_wobble(phase_s + 2, 85.0, 8.0)), 1),
        "flight_time_s": round(phase_s, 1),
        "heading_deg": round(_simulated_wobble(phase_s + 3, 0.0, 45.0), 1),
        "system_health": {
            "battery": round(_simulated_wobble(phase_s + 4, 92.0, 3.0), 1),
            "avionics": round(_simulated_wobble(phase_s + 5, 96.0, 2.0), 1),
            "payload": round(_simulated_wobble(phase_s + 6, 90.0, 4.0), 1),
            "communications": round(_simulated_wobble(phase_s + 7, 98.0, 1.0), 1),
            "navigation": round(_simulated_wobble(phase_s + 8, 94.0, 2.0), 1),
        },
        "notes": (
            "All values are simulated/fictional for visualization and dashboard "
            "development. Not real telemetry. Not connected to any real aircraft, "
            "sensor, or control hardware."
        ),
    }


def write_telemetry_file(
    path: Path | str | None = None,
    count: int = 5,
) -> Path:
    """Write simulated telemetry samples to a JSON file and return its path."""
    if path is None:
        path = Path(__file__).resolve().parent / "telemetry_sim.json"
    path = Path(path)
    records = [simulated_telemetry(phase_s=float(i * 30)) for i in range(count)]
    path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path


def main() -> None:
    path = write_telemetry_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"wrote {len(data)} simulated telemetry records to {path}")
    print(f"sample record keys: {sorted(data[0].keys())}")


if __name__ == "__main__":
    main()
