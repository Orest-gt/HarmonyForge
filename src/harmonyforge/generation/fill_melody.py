"""
Fill Melody Generator.
Creates textural pad / arpeggiated fills that sit behind the lead melody and provide harmonic motion.
"""

import random
from typing import List

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.theory.harmony import safe_pitch_to_midi
from harmonyforge.generation.melody_generator import MelodyEvent, select_weighted_pitch


def generate_fill_melody(
    progression_midi: List[List[int]],
    scale_name: str,
    key_root: str,
    style: StyleSignature,
    bpm: int,
) -> List[MelodyEvent]:
    """Generates a fill/pad stem for harmonic motion and texture."""
    if config.seed is not None:
        rng = random.Random(config.seed + 300)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = safe_pitch_to_midi(key_root, octave=3)

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=4)

    # Fill notes live in the lower-middle texture range, but can also rise
    # into the upper pad register for brighter styles.
    if style.darkness_level > 0.6:
        fill_notes = [n for n in all_scale_notes if 50 <= n <= 74]
    else:
        fill_notes = [n for n in all_scale_notes if 55 <= n <= 80]
    if not fill_notes:
        fill_notes = all_scale_notes or [root_midi]

    total_bars = len(progression_midi)
    prev_pitch = fill_notes[len(fill_notes) // 2]
    current_beat = 0.0

    while current_beat < total_bars * 4.0:
        bar_idx = min(int(current_beat // 4.0), total_bars - 1)
        chord = progression_midi[bar_idx]

        # Create long sustained pads with occasional shorter harmonic flares.
        if current_beat % 4.0 == 0.0:
            dur = 3.5 if rng.random() < 0.8 else 2.5
        else:
            dur = 1.5 if rng.random() < 0.4 else 0.95
        if current_beat + dur > total_bars * 4.0:
            dur = max(1.0, total_bars * 4.0 - current_beat)

        pitch = select_weighted_pitch(prev_pitch, fill_notes, chord, style, rng)
        velocity = rng.randint(60, 85) if style.darkness_level > 0.6 else rng.randint(75, 95)

        # Occasionally create arpeggio-like flares on offbeats.
        if current_beat % 4.0 != 0.0 and rng.random() < 0.30:
            dur = 0.5
            pitch = select_weighted_pitch(prev_pitch, fill_notes, chord, style, rng)
            velocity = max(60, velocity - 10)

        events.append(MelodyEvent(
            midi_note=pitch,
            start_beat=current_beat,
            duration_beats=dur * 0.95,
            velocity=velocity,
        ))
        prev_pitch = pitch
        current_beat += dur

    return events
