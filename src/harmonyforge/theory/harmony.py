"""
Core harmony logic: chord generation, modal interchange, etc.
"""

from typing import List
from harmonyforge.theory.scales import get_scale, get_notes_in_scale
from harmonyforge.theory.chords import get_chord, construct_chord_notes

def get_diatonic_chords(root_midi: int, scale_name: str, chord_type: str = "triad") -> List[List[int]]:
    """
    Builds diatonic chords (triads or 7ths) for each degree of the scale.
    Note: A naive implementation stacking 3rds within the scale degrees.
    """
    scale = get_scale(scale_name)
    # Get 2 octaves to safely build chords on upper degrees
    scale_notes = get_notes_in_scale(root_midi, scale, octaves=2)
    
    chords = []
    # Only iterate through the first octave (the 7 degrees)
    degrees_count = len(scale.intervals)
    steps = 3 if chord_type == "triad" else 4 # 3 notes for triad, 4 for 7th
    
    for i in range(degrees_count):
        chord_notes = [scale_notes[i + (j * 2)] for j in range(steps)]
        chords.append(chord_notes)
        
    return chords

def get_secondary_dominant(target_chord_root: int) -> List[int]:
    """
    Returns the V7 chord of the target chord root.
    Target chord root should be a MIDI note.
    """
    # V is 7 semitones up (a perfect 5th)
    dominant_root = target_chord_root + 7
    dom7_template = get_chord("dom7")
    return construct_chord_notes(dominant_root, dom7_template)
