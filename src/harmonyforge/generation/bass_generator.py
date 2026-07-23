"""
808 Bass generator v1.2 — Producer Edition.

Key producer features:
  1. Sustained 808 hits on beat 1 with natural breathing gaps.
  2. Syncopated sub-hits anticipating the next bar.
  3. Turnaround 808 Triplet Rolls (16th-triplet sub-hits at bar 4 & 8).
  4. Real pitch bend slides with variable bend depth.
  5. Octave jump pops (Tay Keith / Metro Boomin signature).
"""

import random
from typing import List, Optional
from pydantic import BaseModel

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature


class BassEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int
    pitch_bend: int = 0  # 0 = no bend, -8192 to 8191


def generate_808_pattern(
    progression_midi: List[List[int]],
    style: StyleSignature,
    bpm: int,
) -> List[BassEvent]:
    """
    Generates an authentic 808 bass stem with sustained hits, syncopated sub-hits,
    turnaround 808 rolls, and pitch-bend slides.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()

    events: List[BassEvent] = []
    prev_bass_pitch: Optional[int] = None

    for i, chord in enumerate(progression_midi):
        # Transpose chord tones to bass register (C1 to C3 — MIDI 24-48)
        bass_candidates: List[int] = []
        for pitch in chord:
            p = pitch
            while p > 48:
                p -= 12
            while p < 24:
                p += 12
            bass_candidates.append(p)

        root_bass = bass_candidates[0]
        bar_start = i * 4.0
        next_bar_start = (i + 1) * 4.0

        # --- BEAT 1: ROOT / PEDAL ANCHOR ---
        current_chord_pcs = [p % 12 for p in chord]
        current_chord_tones = [p for p in bass_candidates if p % 12 in current_chord_pcs]

        if (prev_bass_pitch is not None
                and rng.random() > style.root_anchor_prob
                and rng.random() < style.repetition_tendency
                and prev_bass_pitch % 12 in current_chord_pcs):
            beat1_pitch = prev_bass_pitch   # Pedal point only when it still fits the current chord
        elif rng.random() <= style.root_anchor_prob:
            beat1_pitch = root_bass          # Root (most common)
        elif current_chord_tones:
            beat1_pitch = min(current_chord_tones, key=lambda p: abs(p - (prev_bass_pitch or root_bass)))
        else:
            beat1_pitch = rng.choice(bass_candidates)  # 3rd or 5th

        prev_bass_pitch = beat1_pitch

        # --- BEAT 1 SUSTAIN DURATION ---
        if style.syncopation_level > 0.7:
            beat1_dur = rng.choice([1.5, 1.75, 2.0])
        else:
            beat1_dur = rng.choice([2.0, 2.5, 3.0, 3.5])

        beat1_dur = min(beat1_dur, next_bar_start - bar_start - 0.25)

        velocity = rng.randint(110, 127)   # 808 is loud & punchy
        events.append(BassEvent(
            midi_note=beat1_pitch,
            start_beat=bar_start,
            duration_beats=beat1_dur,
            velocity=velocity
        ))

        # --- TURNAROUND / CADENCE 808 ROLL ---
        is_cadence_bar = (i % 4 == 3)
        next_chord = progression_midi[i + 1] if i + 1 < len(progression_midi) else chord
        next_root = next_chord[0] if next_chord else root_bass
        same_root = next_root % 12 == root_bass % 12

        if is_cadence_bar and style.rhythmic_density > 0.55 and rng.random() < 0.65:
            roll_start = bar_start + 3.25
            roll_step = 0.25 / 3.0
            if not same_root and rng.random() < 0.65:
                roll_pitch = next_root if next_root <= 54 else root_bass
            else:
                roll_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch

            for r_idx in range(3):
                events.append(BassEvent(
                    midi_note=roll_pitch,
                    start_beat=roll_start + (r_idx * roll_step),
                    duration_beats=roll_step * 0.9,
                    velocity=min(127, 94 + (r_idx * 8)),
                    pitch_bend=4096 if r_idx == 2 else 0
                ))

        # --- SYNCOPATED SUB-HIT ---
        elif rng.random() < style.syncopation_level:
            sub_hit_offsets = [2.5, 3.0, 3.5]
            sub_hit_options = [bar_start + o for o in sub_hit_offsets if bar_start + o >= bar_start + beat1_dur + 0.25]
            if not sub_hit_options:
                sub_hit_options = [bar_start + beat1_dur + 0.25]

            sub_beat = rng.choice(sub_hit_options)
            sub_dur = max(0.25, min(next_bar_start - sub_beat - 0.05, 1.25))

            if rng.random() < 0.45:
                sub_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch
            else:
                sub_pitch = beat1_pitch

            if not same_root and rng.random() < 0.45:
                alt_candidates = [p for p in bass_candidates if p % 12 == next_root % 12]
                if alt_candidates:
                    sub_pitch = min(alt_candidates, key=lambda n: abs(n - sub_pitch))

            bend = 0
            if rng.random() < (0.2 + 0.4 * style.syncopation_level):
                bend = rng.choice([2048, 3072, 4096, 6144])

            sub_vel = rng.randint(96, 122)
            events.append(BassEvent(
                midi_note=sub_pitch,
                start_beat=sub_beat,
                duration_beats=sub_dur,
                velocity=sub_vel,
                pitch_bend=bend
            ))

    return events
