"""
Core deterministic generation engine for chord progressions based on Style Signatures.
Features professional voicings (Drop-2 open spread) and style-driven rhythmic chord re-striking.
"""

import random
from typing import List
from pydantic import BaseModel
import music21.pitch

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.harmony import get_diatonic_chords, voice_chord_pro


class ChordEvent(BaseModel):
    midi_notes: List[int]
    start_beat: float
    duration_beats: float
    velocity: int


class ProgressionResult(BaseModel):
    chords_midi: List[List[int]]          # Unvoiced chord triads/7ths for bass/melody reference
    chords_voiced: List[List[int]]        # Open-spread Drop-2 pro voicings
    chord_events: List[ChordEvent]        # Rhythmic chord strikes with durations & velocities
    chords_roman: List[str]
    scale_name: str
    key_root: str
    bpm: int


class ProgressionGenerator:
    def __init__(self, style: StyleSignature):
        self.style = style

    def generate(self, root_note: str, scale_name: str, bars: int = 8) -> ProgressionResult:
        """
        Generates a chord progression guided by the style signature.
        Includes open-spread voicings and style-driven rhythmic chording.
        """
        if config.seed is not None:
            rng = random.Random(config.seed)
        else:
            rng = random.Random()

        root_midi = music21.pitch.Pitch(f"{root_note}3").midi

        # Base diatonic chords (Triads by default, or 7ths if complexity > 0.6)
        chord_type = "7th" if self.style.harmonic_complexity > 0.6 else "triad"
        diatonic_pool = get_diatonic_chords(root_midi, scale_name, chord_type)

        diatonic_roman = ["I", "ii", "iii", "IV", "V", "vi", "vii°"] if scale_name == "major" else ["i", "ii°", "III", "iv", "v", "VI", "VII"]

        # ---------------------------------------------------------------
        # Genre-aware chord movement graphs
        # Keys = chord degree index, values = weighted next-chord choices.
        # Trap/dark: heavily uses i → VII → VI → VII (degrees 0,6,5,6)
        # R&B/soul:  ii → V → I turnaround (1,4,0)
        # Ambient:   slow drifting, prefers vi and IV (5,3)
        # ---------------------------------------------------------------
        is_trap_dark  = (self.style.darkness_level > 0.7 and self.style.syncopation_level > 0.6)
        is_rnb        = (self.style.harmonic_complexity > 0.6 and self.style.darkness_level < 0.6)
        is_ambient    = (self.style.rhythmic_density < 0.4)

        if is_trap_dark:
            # Travis / Metro: i - VII - VI - VII loop, occasionally drops to iv or v
            CHORD_GRAPH = {
                0: [6, 5, 6],          # i  → VII (2x) or VI
                6: [5, 0, 5],          # VII → VI (2x) or i
                5: [6, 4, 6],          # VI  → VII (2x) or v
                4: [0, 5],             # v   → i or VI
                3: [0, 4],             # iv  → i or v
                1: [4, 0],             # ii° → v or i
                2: [0, 5],
            }
        elif is_rnb:
            # Neo-soul / R&B: ii-V-I, iii-vi-IV-V turns
            CHORD_GRAPH = {
                0: [3, 5, 2],
                1: [4, 5],
                2: [5, 1],
                3: [1, 4, 0],
                4: [0, 5],
                5: [1, 3, 4],
                6: [0, 4],
            }
        elif is_ambient:
            # Ambient: slow, stays near vi and IV, avoids V
            CHORD_GRAPH = {
                0: [5, 3],
                3: [5, 0],
                5: [3, 0],
                4: [0, 5],
                1: [0, 3],
                2: [5, 0],
                6: [0, 5],
            }
        else:
            # Generic diatonic pop/default
            CHORD_GRAPH = {
                0: [3, 4, 5],
                1: [4, 5],
                2: [5, 1],
                3: [1, 4, 0],
                4: [0, 5],
                5: [1, 3, 4],
                6: [0, 4],
            }

        progression_raw: List[List[int]] = []
        progression_voiced: List[List[int]] = []
        chord_events: List[ChordEvent] = []
        roman: List[str] = []

        current_chord_idx = 0  # Always start on tonic

        for i in range(bars):
            raw_chord = diatonic_pool[current_chord_idx]
            voiced_chord = voice_chord_pro(raw_chord, self.style)

            progression_raw.append(raw_chord)
            progression_voiced.append(voiced_chord)
            roman.append(diatonic_roman[current_chord_idx])

            # --- Rhythmic chord strike pattern ---
            bar_start_beat = i * 4.0

            if self.style.syncopation_level > 0.65:
                # Metro Boomin syncopated bounce: lands on 1 and the & of 2
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 0.0,
                    duration_beats=1.5,
                    velocity=95
                ))
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 2.5,
                    duration_beats=1.25,
                    velocity=85
                ))
            elif self.style.rhythmic_density > 0.75:
                # Rage / Drill staccato stabs
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 0.0,
                    duration_beats=0.5,
                    velocity=105
                ))
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 2.5,
                    duration_beats=0.5,
                    velocity=95
                ))
            else:
                # Ambient sustained pad / swell
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 0.0,
                    duration_beats=3.8,
                    velocity=90
                ))

            # --- Next chord selection ---
            # With repetition_tendency: hold the chord on odd bars
            if rng.random() < self.style.repetition_tendency and i > 0 and i % 2 != 0:
                pass  # Hold current chord (repetition — very trap)
            else:
                choices = CHORD_GRAPH.get(current_chord_idx, [0, 3, 5])
                choices = [c for c in choices if c < len(diatonic_pool)]
                if not choices:
                    choices = [0]
                current_chord_idx = rng.choice(choices)

        bpm = rng.randint(self.style.preferred_bpm_range[0], self.style.preferred_bpm_range[1])

        return ProgressionResult(
            chords_midi=progression_raw,
            chords_voiced=progression_voiced,
            chord_events=chord_events,
            chords_roman=roman,
            scale_name=scale_name,
            key_root=root_note,
            bpm=bpm
        )
