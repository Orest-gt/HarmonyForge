"""
Core harmony logic: chord generation, pro voicings (drop-2, open spread), modal interchange, etc.
"""

from typing import List
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.theory.chords import get_chord, construct_chord_notes


def get_diatonic_chords(root_midi: int, scale_name: str, chord_type: str = "triad") -> List[List[int]]:
    """
    Builds diatonic chords (triads or 7ths) for each degree of the scale.
    """
    scale = get_scale(scale_name)
    scale_notes = get_notes_in_scale(root_midi, scale, octaves=2)

    chords = []
    degrees_count = len(scale.intervals)
    steps = 3 if chord_type == "triad" else 4

    for i in range(degrees_count):
        chord_notes = [scale_notes[i + (j * 2)] for j in range(steps)]
        chords.append(chord_notes)

    return chords


def voice_chord_pro(chord_notes: List[int], style: StyleSignature) -> List[int]:
    """
    Transforms a naive closed chord (e.g. [C4, E4, G4, B4]) into a professional
    open-spread Drop-2 keyboard voicing:
      - Left Hand Bass: Root/5th in octave 3 (MIDI 48-60)
      - Right Hand Guide Tones: 3rd & 7th in octave 4 (MIDI 60-72)
      - Top Extension / Color Note: 9th/5th in octave 4-5 (MIDI 67-79)
    """
    if not chord_notes:
        return [60, 64, 67]

    root_pc = chord_notes[0] % 12
    pcs = [n % 12 for n in chord_notes]

    # 1. Bass Anchor (Left Hand: Root in MIDI 48-60)
    lh_bass = root_pc + 48
    if lh_bass < 48:
        lh_bass += 12

    # 2. Guide Tones (3rd and 7th/5th) in Right Hand (MIDI 60-72)
    rh_notes = []
    for pc in pcs[1:]:
        p = pc + 60
        if p < 60:
            p += 12
        rh_notes.append(p)

    # 3. Drop-2 / Open Spread: If harmonic_complexity > 0.5, spread the top note up an octave
    if style.harmonic_complexity > 0.5 and len(rh_notes) >= 2:
        # Move highest note up an octave for wide synth/piano spread
        rh_notes[-1] += 12

    # 4. Optional 9th color extension if high complexity
    if style.harmonic_complexity > 0.7:
        ninth_pc = (root_pc + 2) % 12
        ninth_pitch = ninth_pc + 72
        rh_notes.append(ninth_pitch)

    voiced = sorted(list(set([lh_bass] + rh_notes)))
    return voiced


def get_secondary_dominant(target_chord_root: int) -> List[int]:
    """
    Returns the V7 chord of the target chord root.
    """
    dominant_root = target_chord_root + 7
    dom7_template = get_chord("dom7")
    return construct_chord_notes(dominant_root, dom7_template)
