"""
Vocal Topline Generator Mode.
Generates human-singable melody lines adhering to strict vocal constraints:
  1. Breath pause insertion every 2-4 bars.
  2. Singable range restriction (<= 14 semitones).
  3. Syllabic natural rhythm (8th, quarter, half notes).
"""

import random
from typing import List

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.generation.melody_generator import MelodyEvent, select_weighted_pitch


def generate_vocal_topline(
    progression_midi: List[List[int]],
    scale_name: str,
    key_root: str,
    style: StyleSignature,
    bpm: int
) -> List[MelodyEvent]:
    """
    Generates a vocal topline adhering to human singing ergonomics:
    breath gaps, narrow singable register, and syllabic note lengths.
    """
    if config.seed is not None:
        rng = random.Random(config.seed + 200)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=2)

    # Singable range restriction: 14 semitones max (e.g. C4 to D5 / 60 to 74)
    vocal_scale_notes = [n for n in all_scale_notes if 60 <= n <= 74]
    if not vocal_scale_notes:
        vocal_scale_notes = [root_midi]

    total_bars = len(progression_midi)
    current_beat = 0.0

    prev_pitch = vocal_scale_notes[len(vocal_scale_notes) // 2]  # Center of range

    for bar_i in range(total_bars):
        chord_i = progression_midi[bar_i]

        # 1. Breath Pause Check: Rest on the last beat of every 2nd bar
        is_breath_bar = (bar_i % 2 == 1)
        bar_start_beat = bar_i * 4.0
        current_beat = bar_start_beat

        # Syllabic rhythm options for vocal line (quarter, 8th, half notes)
        vocal_durs = [0.5, 0.5, 1.0, 1.0, 2.0]

        while current_beat < (bar_start_beat + (3.0 if is_breath_bar else 4.0)):
            dur = rng.choice(vocal_durs)
            if current_beat + dur > (bar_start_beat + 4.0):
                dur = (bar_start_beat + 4.0) - current_beat
                if dur <= 0:
                    break

            snapped_beat = round(current_beat * 4.0) / 4.0

            # Pitch selection (strongly stepwise & chord tone resolved)
            pitch = select_weighted_pitch(prev_pitch, vocal_scale_notes, chord_i, style, rng)

            # Downbeat resolution on beat 1
            if snapped_beat % 4.0 == 0.0:
                chord_pcs = [c % 12 for c in chord_i]
                chord_tones = [n for n in vocal_scale_notes if n % 12 in chord_pcs]
                if chord_tones:
                    pitch = min(chord_tones, key=lambda n: abs(n - pitch))

            events.append(MelodyEvent(
                midi_note=pitch,
                start_beat=snapped_beat,
                duration_beats=dur * 0.85,
                velocity=rng.randint(80, 105)
            ))
            prev_pitch = pitch
            current_beat += dur

    return events
