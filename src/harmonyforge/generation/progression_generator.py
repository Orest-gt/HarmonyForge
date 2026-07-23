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

        progression_raw: List[List[int]] = []
        progression_voiced: List[List[int]] = []
        chord_events: List[ChordEvent] = []
        roman: List[str] = []

        current_chord_idx = 0  # Start on tonic

        for i in range(bars):
            raw_chord = diatonic_pool[current_chord_idx]
            voiced_chord = voice_chord_pro(raw_chord, self.style)

            progression_raw.append(raw_chord)
            progression_voiced.append(voiced_chord)
            roman.append(diatonic_roman[current_chord_idx])

            # Generate rhythmic chord strikes for this bar
            bar_start_beat = i * 4.0

            if self.style.syncopation_level > 0.65:
                # Syncopated bounce pattern (e.g. Metro Boomin / Nick Mira)
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
                # Staccato synth stabs (e.g. Rage / Drill)
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
                # Standard sustained pad / ambient swell
                chord_events.append(ChordEvent(
                    midi_notes=voiced_chord,
                    start_beat=bar_start_beat + 0.0,
                    duration_beats=3.8,
                    velocity=90
                ))

            # Decide next chord index
            if rng.random() < self.style.repetition_tendency and i > 0 and i % 2 != 0:
                current_chord_idx = current_chord_idx
            else:
                if current_chord_idx == 0:
                    choices = [3, 4, 5]
                elif current_chord_idx in [3, 5]:
                    choices = [1, 4]
                elif current_chord_idx == 4:
                    choices = [0, 5]
                else:
                    choices = [0, 3, 4]

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
