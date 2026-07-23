"""
MIDI Humanization & Genre Swing Templates.
Adds authentic micro-timing swing curves, laid-back Dilla feel, Drill push, and velocity humanization.
"""

import random
import pretty_midi

# Swing Styles
SWING_TEMPLATES = {
    "straight":    {"swing_16th": 0.00,  "lag": 0.000, "jitter": 0.008},
    "trap_bounce": {"swing_16th": 0.018, "lag": 0.005, "jitter": 0.012},
    "dilla_swing": {"swing_16th": 0.035, "lag": 0.025, "jitter": 0.018},  # Laid back behind the beat
    "drill_push":  {"swing_16th": -0.012,"lag": -0.005,"jitter": 0.010},  # Aggressive forward momentum
    "afro_triplet":{"swing_16th": 0.025, "lag": 0.010, "jitter": 0.015},
}


def humanize_instrument(
    inst: pretty_midi.Instrument,
    style_name: str = "straight",
    timing_variance: float = 0.012,
    velocity_variance: int = 8,
    bpm: float = 120.0
) -> None:
    """
    Applies authentic genre swing templates and humanization to a pretty_midi instrument.
    """
    template = SWING_TEMPLATES.get(style_name.lower(), SWING_TEMPLATES["straight"])
    beat_dur = 60.0 / bpm

    for note in inst.notes:
        start_beat = note.start / beat_dur
        sixteenth_step = int(round(start_beat * 4.0)) % 4

        # 1. Swing offset (off-beat 16ths: steps 1 and 3)
        swing_offset = 0.0
        if sixteenth_step in [1, 3]:
            swing_offset = template["swing_16th"]

        # 2. General lag / push behind or ahead of beat
        lag_offset = template["lag"]

        # 3. Micro-jitter
        jitter = random.uniform(-template["jitter"], template["jitter"])

        total_offset = swing_offset + lag_offset + jitter

        note.start = max(0.0, note.start + total_offset)
        note.end = max(note.start + 0.05, note.end + total_offset + random.uniform(-0.005, 0.005))

        # Velocity humanization
        vel_shift = random.randint(-velocity_variance, velocity_variance)
        note.velocity = max(1, min(127, note.velocity + vel_shift))
