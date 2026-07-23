"""
808 Bass generator.
Creates trap-authentic patterns: sustained 808 hits, syncopated sub-hits,
realistic pitch bend slides (not always full-range), and root anchoring.
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
) -> List["BassEvent"]:
    """
    Generates a trap-style 808 pattern.

    Key professional behaviours:
    - Beat-1 anchor: sustained hit (1.5 – 3.5 beats) so the 808 "breathes" and sustains.
    - Syncopated sub-hit: lands at .5 position (1.5 / 2.5 / 3.5) before the next bar.
    - Pitch bend slide: uses variable bend depth (not always max) and fires AFTER note start.
    - Pedal point: with high repetition_tendency, keeps the same root across bars.
    - Octave jump: stylistic pop used in Travis/Metro @ ~35% probability.
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
        # Next bar start (or total end) — used to clamp durations
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
        # Trap 808s sustain. Duration = either to end of bar OR just before the syncopated hit.
        # High syncopation → shorter sustain (room for syncopated hit)
        if style.syncopation_level > 0.7:
            # Will likely have a sub-hit, so sustain ~1.5-2 beats
            beat1_dur = rng.choice([1.5, 1.75, 2.0])
        else:
            # Sparser style — long sustain across most of the bar
            beat1_dur = rng.choice([2.0, 2.5, 3.0, 3.5])

        # Clamp: don't bleed into next bar (leave at least 0.25 gap)
        beat1_dur = min(beat1_dur, next_bar_start - bar_start - 0.25)

        velocity = rng.randint(110, 127)   # 808 is loud
        events.append(BassEvent(
            midi_note=beat1_pitch,
            start_beat=bar_start,
            duration_beats=beat1_dur,
            velocity=velocity
        ))

        # --- SYNCOPATED SUB-HIT ---
        if rng.random() < style.syncopation_level:
            # Typical trap 808 sub-hit positions: anticipates the next bar
            sub_hit_options = [bar_start + 2.5, bar_start + 3.0, bar_start + 3.5]
            # Must not overlap with the beat-1 sustain
            sub_hit_options = [b for b in sub_hit_options if b >= bar_start + beat1_dur]
            if not sub_hit_options:
                sub_hit_options = [bar_start + beat1_dur + 0.25]

            sub_beat = rng.choice(sub_hit_options)
            sub_dur = next_bar_start - sub_beat - 0.05   # Run to bar end, slight gap
            sub_dur = max(0.25, min(sub_dur, 1.5))       # Clamp to [0.25, 1.5]

            # Pitch: octave jump (Travis signature) or same root
            if rng.random() < 0.35:
                sub_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch
            else:
                sub_pitch = beat1_pitch

            # Pitch bend slide — variable depth, not always full range
            # Real slides: partial bend feels more natural than always 8191
            bend = 0
            if rng.random() < (0.15 + 0.4 * style.syncopation_level):
                # Variable bend depth: small (2048), medium (4096), big (6144), full (8191)
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
