"""
MIDI Humanization & Tempo-Relative Genre Swing Templates.
Scales micro-timing swing curves dynamically with BPM for authentic Dilla drag, Trap bounce, and Drill push.

Rules:
  - Swing offset (offbeat 16th push/drag) only applies to off-beat 16th positions (steps 1 and 3).
  - Global lag/push NEVER applies to the downbeat (step 0) — this keeps the harmonic anchor locked.
  - Chord pads receive a reduced swing strength (20% of full) via the `swing_strength` parameter.
"""

import random
from typing import Dict
import pretty_midi

# Swing percentages relative to 16th-note grid duration.
# swing_pct: offset for off-beat 16th notes (steps 1, 3)
# lag_pct:   global pull/push BEHIND or AHEAD of beat (NOT applied to beat 1 / step 0)
# jitter_sec: absolute micro-jitter in seconds (human imprecision)
SWING_TEMPLATES: Dict[str, Dict[str, float]] = {
    "straight":    {"swing_pct": 0.00,  "lag_pct": 0.00,  "jitter_sec": 0.006},
    "trap_bounce": {"swing_pct": 0.12,  "lag_pct": 0.03,  "jitter_sec": 0.010},  # 12% offbeat 16th push
    "dilla_swing": {"swing_pct": 0.22,  "lag_pct": 0.12,  "jitter_sec": 0.015},  # 22% lazy Dilla drag
    "drill_push":  {"swing_pct": -0.10, "lag_pct": -0.04, "jitter_sec": 0.008},  # 10% ahead-of-beat momentum
    "afro_triplet":{"swing_pct": 0.18,  "lag_pct": 0.05,  "jitter_sec": 0.012},
}


def humanize_instrument(
    inst: pretty_midi.Instrument,
    style_name: str = "straight",
    timing_variance: float = 0.012,
    velocity_variance: int = 8,
    bpm: float = 120.0,
    swing_strength: float = 1.0,   # [0.0 – 1.0] scalar. Chords should use ~0.2 to keep pads locked.
) -> None:
    """
    Applies tempo-aware genre swing templates and humanization to a pretty_midi instrument.

    Key behaviour:
    - Swing offset only hits off-beat 16th positions (1 and 3 within each beat).
    - Global lag (e.g. Dilla's lazy pocket) is NEVER applied to the downbeat (position 0),
      preserving the harmonic anchor so the groove doesn't drift.
    - `swing_strength` scales ALL swing/lag effects, allowing chords to stay near-straight
      while the melody receives the full genre swing.
    """
    template = SWING_TEMPLATES.get(style_name.lower(), SWING_TEMPLATES["straight"])
    beat_dur = 60.0 / bpm
    grid_16th_dur = beat_dur / 4.0

    for note in inst.notes:
        # 16th-note position within the current beat (0, 1, 2, 3)
        start_beat_f = note.start / beat_dur
        sixteenth_step = int(round(start_beat_f * 4.0)) % 4

        # 1. Swing offset — ONLY on off-beat 16ths (1 and 3)
        swing_offset = 0.0
        if sixteenth_step in [1, 3]:
            swing_offset = grid_16th_dur * template["swing_pct"] * swing_strength

        # 2. Global lag/push — NEVER on downbeat (step 0 of each beat)
        lag_offset = 0.0
        if sixteenth_step != 0:
            lag_offset = grid_16th_dur * template["lag_pct"] * swing_strength

        # 3. Micro-jitter (always scaled by swing_strength so pads are tighter)
        jitter = random.uniform(
            -template["jitter_sec"] * swing_strength,
             template["jitter_sec"] * swing_strength,
        )

        total_offset = swing_offset + lag_offset + jitter

        note.start = max(0.0, note.start + total_offset)
        note.end   = max(note.start + 0.05, note.end + total_offset + random.uniform(-0.005, 0.005))

        # Velocity humanization
        vel_shift = random.randint(-velocity_variance, velocity_variance)
        note.velocity = max(1, min(127, note.velocity + vel_shift))
