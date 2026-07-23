"""
Melody generator.
Uses style-driven weighted contour motion and flexible phrase/motif memory.
"""

import random
from typing import List
from pydantic import BaseModel

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale

class MelodyEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int


def select_weighted_pitch(
    prev_pitch: int,
    scale_notes: List[int],
    current_chord: List[int],
    style: StyleSignature,
    rng: random.Random
) -> int:
    """
    Selects the next pitch using a style-driven weighted contour motion.
    High weight for stepwise motion (1-3 semitones) and chord tones,
    controlled weight for intentional octave/stylistic leaps.
    """
    if not scale_notes:
        return prev_pitch

    weights: List[float] = []
    chord_pcs = [c % 12 for c in current_chord]

    for note in scale_notes:
        interval = abs(note - prev_pitch)

        # 1. Base contour weight based on semitone distance
        if interval == 0:
            # Pedal point / pitch repetition (biased by repetition_tendency)
            w = 4.0 * style.repetition_tendency
        elif 1 <= interval <= 3:
            # Stepwise motion (most natural melodic movement)
            w = 8.0
        elif 4 <= interval <= 5:
            # Small skip
            w = 4.0
        elif 6 <= interval <= 7:
            # Perfect 4th/5th / tritone leap
            w = 2.5
        elif interval == 12:
            # Stylistic octave leap (e.g. Rage / Trap octave pop)
            w = 3.5 * style.dissonance_tolerance
        else:
            # Large unmusical leaps (> 7, except octave) get low weight
            w = 0.3 * max(0.1, 1.0 - (interval / 24.0))

        # 2. Chord tone bonus
        if note % 12 in chord_pcs:
            w *= 2.2

        weights.append(max(0.01, w))

    return rng.choices(scale_notes, weights=weights)[0]


def generate_melody(progression_midi: List[List[int]], scale_name: str, key_root: str, style: StyleSignature, bpm: int) -> List[MelodyEvent]:
    """
    Generates a lead melody based on the underlying progression and scale,
    using weighted contour sampling and flexible 2-bar motif memory (A-A'-A-B form).
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=3)
    
    # Restrict melody range to a musical register (C4 to C6 / 60 to 84)
    scale_notes = [n for n in all_scale_notes if 60 <= n <= 84]
    if not scale_notes:
        scale_notes = [root_midi]

    # --- 1. GENERATE 2-BAR MOTIF (PHRASE A) ---
    motif_rhythm: List[float] = []
    beats_left = 8.0
    step_options = [0.25, 0.5, 1.0] if style.rhythmic_density > 0.5 else [0.5, 1.0, 2.0]

    while beats_left > 0:
        dur = rng.choice(step_options)
        if dur > beats_left:
            dur = beats_left
        motif_rhythm.append(dur)
        beats_left -= dur

    # Generate 2-bar motif pitch pattern using weighted contour
    motif_pitches: List[int] = []
    first_chord = progression_midi[0] if progression_midi else [root_midi]
    first_chord_pcs = [c % 12 for c in first_chord]
    chord_tones = [n for n in scale_notes if n % 12 in first_chord_pcs]
    prev_p = rng.choice(chord_tones if chord_tones else scale_notes)

    for _ in motif_rhythm:
        next_p = select_weighted_pitch(prev_p, scale_notes, first_chord, style, rng)
        motif_pitches.append(next_p)
        prev_p = next_p

    # --- 2. GENERATE FULL PROGRESSION (A - A' - A - B STRUCTURAL MEMORY) ---
    total_bars = len(progression_midi)
    two_bar_blocks = max(1, (total_bars + 1) // 2)

    for block_idx in range(two_bar_blocks):
        block_start_bar = block_idx * 2
        block_beat_offset = block_start_bar * 4.0

        # Form selection: Block 0=A, Block 1=A', Block 2=A or A'', Last Block=B
        if block_idx == 0:
            form = "A"
        elif block_idx == two_bar_blocks - 1 and two_bar_blocks > 1:
            form = "B"  # Cadential resolution
        else:
            form = "A_prime" if rng.random() < style.repetition_tendency else "A"

        current_beat = block_beat_offset
        note_idx = 0

        for dur in motif_rhythm:
            if note_idx >= len(motif_pitches):
                break

            base_pitch = motif_pitches[note_idx]
            bar_offset = int(current_beat // 4.0)
            chord_i = progression_midi[bar_offset] if bar_offset < len(progression_midi) else progression_midi[-1]

            # Apply variation strategy based on phrase form
            if form == "A":
                note_pitch = base_pitch
            elif form == "A_prime":
                # Controlled mutation: 30% chance to vary note pitch via contour, else keep motif
                if rng.random() < 0.35:
                    note_pitch = select_weighted_pitch(base_pitch, scale_notes, chord_i, style, rng)
                else:
                    note_pitch = base_pitch
            elif form == "B":
                # Cadential phrase / resolution
                if rng.random() < 0.60:
                    note_pitch = select_weighted_pitch(base_pitch, scale_notes, chord_i, style, rng)
                else:
                    note_pitch = base_pitch

            # Density gate (resting chance)
            if rng.random() > (0.20 + 0.70 * style.rhythmic_density):
                current_beat += dur
                note_idx += 1
                continue

            vel = rng.randint(75, 110)
            events.append(MelodyEvent(
                midi_note=note_pitch,
                start_beat=current_beat,
                duration_beats=dur * 0.9,
                velocity=vel
            ))
            current_beat += dur
            note_idx += 1

    return events
