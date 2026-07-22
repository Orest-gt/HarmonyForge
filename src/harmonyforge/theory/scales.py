"""
Music theory definitions for scales and modes.
"""

from typing import List, Dict
from pydantic import BaseModel

class ScaleTemplate(BaseModel):
    name: str
    intervals: List[int] # Intervals from root in semitones (e.g., [0, 2, 4, 5, 7, 9, 11] for Major)

# Standard Diatonic Modes
MAJOR = ScaleTemplate(name="Major", intervals=[0, 2, 4, 5, 7, 9, 11])
IONIAN = MAJOR
DORIAN = ScaleTemplate(name="Dorian", intervals=[0, 2, 3, 5, 7, 9, 10])
PHRYGIAN = ScaleTemplate(name="Phrygian", intervals=[0, 1, 3, 5, 7, 8, 10])
LYDIAN = ScaleTemplate(name="Lydian", intervals=[0, 2, 4, 6, 7, 9, 11])
MIXOLYDIAN = ScaleTemplate(name="Mixolydian", intervals=[0, 2, 4, 5, 7, 10, 11])
MINOR = ScaleTemplate(name="Natural Minor", intervals=[0, 2, 3, 5, 7, 8, 10])
AEOLIAN = MINOR
LOCRIAN = ScaleTemplate(name="Locrian", intervals=[0, 1, 3, 5, 6, 8, 10])

# Harmonic / Melodic
HARMONIC_MINOR = ScaleTemplate(name="Harmonic Minor", intervals=[0, 2, 3, 5, 7, 8, 11])
MELODIC_MINOR = ScaleTemplate(name="Melodic Minor", intervals=[0, 2, 3, 5, 7, 9, 11])

# Pentatonic & Blues
MINOR_PENTATONIC = ScaleTemplate(name="Minor Pentatonic", intervals=[0, 3, 5, 7, 10])
MAJOR_PENTATONIC = ScaleTemplate(name="Major Pentatonic", intervals=[0, 2, 4, 7, 9])
BLUES = ScaleTemplate(name="Blues", intervals=[0, 3, 5, 6, 7, 10])

# Exotic / Advanced
PHRYGIAN_DOMINANT = ScaleTemplate(name="Phrygian Dominant", intervals=[0, 1, 4, 5, 7, 8, 10])
WHOLE_TONE = ScaleTemplate(name="Whole Tone", intervals=[0, 2, 4, 6, 8, 10])
OCTATONIC_HW = ScaleTemplate(name="Octatonic (Half-Whole)", intervals=[0, 1, 3, 4, 6, 7, 9, 10])
OCTATONIC_WH = ScaleTemplate(name="Octatonic (Whole-Half)", intervals=[0, 2, 3, 5, 6, 8, 9, 11])
DOUBLE_HARMONIC = ScaleTemplate(name="Double Harmonic", intervals=[0, 1, 4, 5, 7, 8, 11])
HUNGARIAN_MINOR = ScaleTemplate(name="Hungarian Minor", intervals=[0, 2, 3, 6, 7, 8, 11])

SCALES_DB: Dict[str, ScaleTemplate] = {
    "major": MAJOR,
    "minor": MINOR,
    "harmonic_minor": HARMONIC_MINOR,
    "melodic_minor": MELODIC_MINOR,
    "dorian": DORIAN,
    "phrygian": PHRYGIAN,
    "lydian": LYDIAN,
    "mixolydian": MIXOLYDIAN,
    "locrian": LOCRIAN,
    "minor_pentatonic": MINOR_PENTATONIC,
    "major_pentatonic": MAJOR_PENTATONIC,
    "blues": BLUES,
    "phrygian_dominant": PHRYGIAN_DOMINANT,
    "whole_tone": WHOLE_TONE,
    "octatonic": OCTATONIC_WH,
    "double_harmonic": DOUBLE_HARMONIC,
    "hungarian_minor": HUNGARIAN_MINOR
}

def get_scale(name: str) -> ScaleTemplate:
    """Retrieve a scale template by name."""
    clean_name = name.lower().replace(" ", "_").replace("-", "_")
    if clean_name not in SCALES_DB:
        raise ValueError(f"Scale '{name}' not found.")
    return SCALES_DB[clean_name]

def get_notes_in_scale(root_midi: int, scale: ScaleTemplate, octaves: int = 1) -> List[int]:
    """Get all MIDI notes for a given root and scale, spanning N octaves."""
    notes = []
    for oct_idx in range(octaves):
        base = root_midi + (oct_idx * 12)
        notes.extend([base + interval for interval in scale.intervals])
    return notes
