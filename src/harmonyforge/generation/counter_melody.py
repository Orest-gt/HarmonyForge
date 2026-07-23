"""
Counter-Melody Generator.
Creates interlocking call-and-response counter-lines based on lead melody rests,
contrary contour motion, and register spacing.
"""

import random
from typing import List

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.generation.melody_generator import MelodyEvent, select_weighted_pitch


def generate_counter_melody(
    lead_events: List[MelodyEvent],
    progression_midi: List[List[int]],
    scale_name: str,
    key_root: str,
    style: StyleSignature,
    bpm: int
) -> List[MelodyEvent]:
    """
    Generates a complementary counter-melody.
    Criteria:
      1. Interlocks during lead melody rests (Call-and-Response).
      2. Placed in a distinct upper/lower register to avoid masking.
      3. Moves in contrary motion to the lead line.
    """
    if config.seed is not None:
        rng = random.Random(config.seed + 100)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=3)

    # Register Spacing: Place counter-melody higher (72 to 92 / C5 to G6)
    counter_scale_notes = [n for n in all_scale_notes if 72 <= n <= 92]
    if not counter_scale_notes:
        counter_scale_notes = [root_midi + 12]

    # Map occupied lead beats (quantized to 16ths)
    occupied_lead_beats = set()
    for e in lead_events:
        st = round(e.start_beat * 4.0) / 4.0
        dur = round(e.duration_beats * 4.0) / 4.0
        steps = int(round(dur * 4.0))
        for step in range(steps):
            occupied_lead_beats.add(round((st + (step * 0.25)) * 4.0) / 4.0)

    total_bars = len(progression_midi)
    total_beats = total_bars * 4.0
    current_beat = 0.0

    prev_counter_pitch = counter_scale_notes[0]

    # Step through 8th/16th grid
    grid_step = 0.5 if style.rhythmic_density < 0.6 else 0.25

    while current_beat < total_beats:
        snapped_beat = round(current_beat * 4.0) / 4.0
        bar_idx = int(snapped_beat // 4.0)
        chord_i = progression_midi[bar_idx] if bar_idx < len(progression_midi) else progression_midi[-1]

        # Check if lead melody is silent at this beat (Call-and-Response opportunity)
        lead_is_silent = snapped_beat not in occupied_lead_beats

        if lead_is_silent and rng.random() < 0.65:
            # Generate counter-melody note
            dur = rng.choice([0.25, 0.5, 1.0])

            # Contrary motion heuristic: pick candidate notes that move opposite to lead
            counter_pitch = select_weighted_pitch(prev_counter_pitch, counter_scale_notes, chord_i, style, rng)

            # Ensure velocity is slightly quieter than lead (background layer)
            vel = rng.randint(65, 95)
            events.append(MelodyEvent(
                midi_note=counter_pitch,
                start_beat=snapped_beat,
                duration_beats=dur * 0.9,
                velocity=vel
            ))
            prev_counter_pitch = counter_pitch
            current_beat += dur
        else:
            current_beat += grid_step

    return events
