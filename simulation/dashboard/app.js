// app.js — Simulated dashboard controller (visual demonstration only).
//
// IMPORTANT: Every value displayed here is artificially generated and marked
// SIMULATED. This is a visual interface demonstration — it does not connect
// to any real aircraft, sensor, or control hardware, and it displays no
// real telemetry.

"use strict";

const byId = (id) => document.getElementById(id);

function setText(id, text) {
  const el = byId(id);
  if (el) el.textContent = text;
}

class SimulatedAircraftDashboard {
  constructor() {
    this.start = Date.now();
    this.update();
    this.interval = setInterval(() => this.update(), 1000);
  }

  elapsedSeconds() {
    return (Date.now() - this.start) / 1000;
  }

  formatClock(seconds) {
    const total = Math.floor(seconds);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    const pad = (n) => String(n).padStart(2, "0");
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
  }

  update() {
    const t = this.elapsedSeconds();

    // Simulated aircraft status values (artificial, not real).
    const altitude = 25 + 12 * Math.sin(t * 0.8) + 2 * Math.sin(t * 2.3);
    const speed = 3 + 12 * Math.abs(Math.sin(t * 0.5 + 0.2));
    const battery = Math.max(5, 98 - t * 0.04);
    const flightSeconds = Math.floor(t);
    const heading = ((25 * Math.sin(t * 0.3)) % 360 + 360) % 360;

    setText("altitude", altitude.toFixed(1) + " m");
    setText("speed", speed.toFixed(1) + " m/s");
    setText("battery", battery.toFixed(0) + "%");
    setText("flightTime", `${Math.floor(flightSeconds / 60)} min ${flightSeconds % 60} s`);
    setText("heading", heading.toFixed(1) + " deg");
    setText("status", Math.random() < 0.05 ? "SIMULATED — HOLD" : "SIMULATED — STABLE");

    // Fictional status display (simulated text panel value).
    setText("displayClock", `TIME: ${this.formatClock(t)} — SIMULATED`);

    // System health meters (simulated values).
    const health = {
      battery: Math.max(10, Math.min(100, 90 + 8 * Math.sin(t))),
      avionics: Math.max(10, Math.min(100, 96 + 2 * Math.sin(t * 0.7))),
      payload: Math.max(10, Math.min(100, 88 + 3 * Math.cos(t * 0.4))),
      communications: Math.max(10, Math.min(100, 97 + 0.5 * Math.sin(t))),
      navigation: Math.max(10, Math.min(100, 93 + 2 * Math.sin(t * 1.1))),
    };
    const meters = [
      ["barBattery", "pctBattery", "battery"],
      ["barAvionics", "pctAvionics", "avionics"],
      ["barPayload", "pctPayload", "payload"],
      ["barComms", "pctComms", "communications"],
      ["barNav", "pctNav", "navigation"],
    ];
    for (const [barId, pctId, key] of meters) {
      const value = health[key];
      const bar = byId(barId);
      const span = bar ? bar.querySelector("span") : null;
      if (span) span.style.width = value + "%";
      setText(pctId, value.toFixed(1) + "%");
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new SimulatedAircraftDashboard();
});
