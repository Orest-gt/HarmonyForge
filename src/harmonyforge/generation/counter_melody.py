"""
Counter-Melody Generator.
Creates interlocking call-and-response counter-lines based on lead melody rests,
with real contrary contour motion tracking and register separation.

Key design criteria:
  1. Interlocks during lead melody rests ONLY (Call-and-Response).
     - Silence detection uses integer 16th-step keys (not floats) to avoid comparison bugs.
  2. Placed in a distinct register: upper (C5-G6) for bright styles, lower (C3-B3) for dark/bass-heavy.
  3. Moves in ACTUAL contrary motion: tracks lead melody direction and biases counter in the opposite direction.
"""

import random
from typing import List

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.generation.melody_generator import MelodyEvent, select_weighted_pitch


def _to_16th_key(beat: float) -> int:
    """Convert a beat-float to an integer 16th-step key (avoids float comparison bugs)."""
    return int(round(beat * 4.0))


def _lead_direction(lead_events: List[MelodyEvent]) -> List[int]:
    """
    Returns a list of +1 (ascending), -1 (descending), 0 (same) values
    representing the melodic direction at each lead event transition.
    Used to drive contrary-motion weighting in the counter.
    """
    directions: List[int] = []
    for i in range(len(lead_events) - 1):
        diff = lead_events[i + 1].midi_note - lead_events[i].midi_note
        directions.append(1 if diff > 0 else (-1 if diff < 0 else 0))
    return directions


def generate_counter_melody(
    lead_events: List[MelodyEvent],
    progression_midi: List[List[int]],
    scale_name: str,
    key_root: str,
    style: StyleSignature,
    bpm: int,
    register: str = "upper",   # "upper" (C5-G6) or "lower" (C3-B3)
) -> List[MelodyEvent]:
    """
    Generates a complementary counter-melody.

    Criteria:
      1. Interlocks during lead melody rests (Call-and-Response).
         Integer 16th-step set prevents float comparison drift.
      2. Distinct register (upper/lower) to avoid frequency masking.
      3. Contrary motion: when lead was ascending, counter biases descending, and vice-versa.
    """
    if config.seed is not None:
        rng = random.Random(config.seed + 100)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=4)

    # --- Register Spacing ---
    if register == "lower":
        # Lower counter (e.g. cello-range / low synth fill) — C3 to B3
        counter_scale_notes = [n for n in all_scale_notes if 48 <= n <= 59]
    else:
        # Upper counter (default) — C5 to G6
        counter_scale_notes = [n for n in all_scale_notes if 72 <= n <= 91]

    if not counter_scale_notes:
        counter_scale_notes = [root_midi + (12 if register == "upper" else -12)]

    # --- Build occupied lead beats as INTEGER 16th-step keys (no float comparison) ---
    occupied_16th_steps: set = set()
    for e in lead_events:
        start_16th = _to_16th_key(e.start_beat)
        dur_16ths  = max(1, int(round(e.duration_beats * 4.0)))
        for step in range(dur_16ths):
            occupied_16th_steps.add(start_16th + step)

    # --- Pre-compute lead direction at each 16th step ---
    # Maps 16th-step key -> lead melodic direction just before that step
    lead_dir_at_step: dict = {}
    directions = _lead_direction(lead_events)
    for i, e in enumerate(lead_events[:-1]):
        start_16th = _to_16th_key(e.start_beat)
        dur_16ths  = max(1, int(round(e.duration_beats * 4.0)))
        for step in range(dur_16ths):
            lead_dir_at_step[start_16th + step] = directions[i]

    # --- Grid walk ---
    total_bars  = len(progression_midi)
    total_16ths = total_bars * 16
    grid_step_16ths = 2 if style.rhythmic_density < 0.6 else 1  # 8th or 16th grid

    prev_counter_pitch = counter_scale_notes[len(counter_scale_notes) // 2]
    step_16th = 0

    while step_16th < total_16ths:
        beat_f       = step_16th / 4.0
        bar_idx      = int(beat_f // 4.0)
        chord_i      = progression_midi[bar_idx] if bar_idx < len(progression_midi) else progression_midi[-1]
        lead_is_silent = step_16th not in occupied_16th_steps

        if lead_is_silent and rng.random() < 0.65:
            # --- Contrary motion: bias toward opposite of lead direction ---
            lead_dir = lead_dir_at_step.get(step_16th, 0)  # +1 / -1 / 0

            if lead_dir != 0 and counter_scale_notes:
                # Build a filtered candidate list biased in the contrary direction
                mid_idx   = counter_scale_notes.index(
                    min(counter_scale_notes, key=lambda n: abs(n - prev_counter_pitch))
                )
                if lead_dir == 1:
                    # Lead went up -> counter biases DOWN (use lower half of register)
                    contrary_pool = counter_scale_notes[:max(1, mid_idx + 1)]
                else:
                    # Lead went down -> counter biases UP (use upper half of register)
                    contrary_pool = counter_scale_notes[min(len(counter_scale_notes) - 1, mid_idx):]
                if not contrary_pool:
                    contrary_pool = counter_scale_notes
            else:
                contrary_pool = counter_scale_notes

            dur_16ths_note = rng.choice([1, 2, 4])  # 16th, 8th, quarter
            dur_beats = dur_16ths_note / 4.0

            counter_pitch = select_weighted_pitch(prev_counter_pitch, contrary_pool, chord_i, style, rng)
            vel           = rng.randint(65, 95)  # Slightly quieter than lead

            events.append(MelodyEvent(
                midi_note=counter_pitch,
                start_beat=beat_f,
                duration_beats=dur_beats * 0.9,
                velocity=vel
            ))
            prev_counter_pitch = counter_pitch
            step_16th += dur_16ths_note
        else:
            step_16th += grid_step_16ths

    return events
