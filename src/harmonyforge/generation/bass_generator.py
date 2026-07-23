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
    total_bars = len(progression_midi)

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
        if (prev_bass_pitch is not None
                and rng.random() > style.root_anchor_prob
                and rng.random() < style.repetition_tendency):
            beat1_pitch = prev_bass_pitch   # Pedal point
        elif rng.random() <= style.root_anchor_prob:
            beat1_pitch = root_bass          # Root (most common)
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

        # --- TURNAROUND 808 ROLL (At Bar 4 or Bar 8 cadence) ---
        is_cadence_bar = (i % 4 == 3)
        if is_cadence_bar and style.rhythmic_density > 0.55 and rng.random() < 0.65:
            # 808 Triplet roll on beat 3.75 (three fast 16th sub-hits)
            roll_start = bar_start + 3.25
            roll_step = 0.25 / 3.0
            roll_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch

            for r_idx in range(3):
                events.append(BassEvent(
                    midi_note=roll_pitch,
                    start_beat=roll_start + (r_idx * roll_step),
                    duration_beats=roll_step * 0.9,
                    velocity=min(127, 95 + (r_idx * 10)),
                    pitch_bend=4096 if r_idx == 2 else 0
                ))

        # --- SYNCOPATED SUB-HIT ---
        elif rng.random() < style.syncopation_level:
            sub_hit_options = [bar_start + 2.5, bar_start + 3.0, bar_start + 3.5]
            sub_hit_options = [b for b in sub_hit_options if b >= bar_start + beat1_dur]
            if not sub_hit_options:
                sub_hit_options = [bar_start + beat1_dur + 0.25]

            sub_beat = rng.choice(sub_hit_options)
            sub_dur = next_bar_start - sub_beat - 0.05
            sub_dur = max(0.25, min(sub_dur, 1.5))

            if rng.random() < 0.35:
                sub_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch
            else:
                sub_pitch = beat1_pitch

            bend = 0
            if rng.random() < (0.15 + 0.4 * style.syncopation_level):
                bend = rng.choice([2048, 3072, 4096, 6144, 8191])

            sub_vel = rng.randint(95, 120)
            events.append(BassEvent(
                midi_note=sub_pitch,
                start_beat=sub_beat,
                duration_beats=sub_dur,
                velocity=sub_vel,
                pitch_bend=bend
            ))

    return events
