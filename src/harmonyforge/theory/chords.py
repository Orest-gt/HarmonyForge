"""
Music theory definitions for chords and extensions.
"""

from typing import List, Dict
from pydantic import BaseModel

class ChordTemplate(BaseModel):
    name: str
    intervals: List[int] # Intervals from root in semitones

# Triads
MAJOR_TRIAD = ChordTemplate(name="Major", intervals=[0, 4, 7])
MINOR_TRIAD = ChordTemplate(name="Minor", intervals=[0, 3, 7])
DIMINISHED_TRIAD = ChordTemplate(name="Diminished", intervals=[0, 3, 6])
AUGMENTED_TRIAD = ChordTemplate(name="Augmented", intervals=[0, 4, 8])

# 7th Chords
MAJOR_7 = ChordTemplate(name="Major 7th", intervals=[0, 4, 7, 11])
MINOR_7 = ChordTemplate(name="Minor 7th", intervals=[0, 3, 7, 10])
DOMINANT_7 = ChordTemplate(name="Dominant 7th", intervals=[0, 4, 7, 10])
HALF_DIMINISHED_7 = ChordTemplate(name="Half-Diminished 7th", intervals=[0, 3, 6, 10]) # m7b5
DIMINISHED_7 = ChordTemplate(name="Diminished 7th", intervals=[0, 3, 6, 9])
MINOR_MAJOR_7 = ChordTemplate(name="Minor-Major 7th", intervals=[0, 3, 7, 11])
AUGMENTED_MAJOR_7 = ChordTemplate(name="Augmented Major 7th", intervals=[0, 4, 8, 11])
AUGMENTED_7 = ChordTemplate(name="Augmented 7th", intervals=[0, 4, 8, 10])

# Extensions (9ths, 11ths, 13ths)
MAJOR_9 = ChordTemplate(name="Major 9th", intervals=[0, 4, 7, 11, 14])
MINOR_9 = ChordTemplate(name="Minor 9th", intervals=[0, 3, 7, 10, 14])
DOMINANT_9 = ChordTemplate(name="Dominant 9th", intervals=[0, 4, 7, 10, 14])
MINOR_11 = ChordTemplate(name="Minor 11th", intervals=[0, 3, 7, 10, 14, 17])
DOMINANT_11 = ChordTemplate(name="Dominant 11th", intervals=[0, 4, 7, 10, 14, 17])

# Sus and Add Chords
SUS_2 = ChordTemplate(name="Sus 2", intervals=[0, 2, 7])
SUS_4 = ChordTemplate(name="Sus 4", intervals=[0, 5, 7])
ADD_9 = ChordTemplate(name="Add 9", intervals=[0, 4, 7, 14])
MINOR_ADD_9 = ChordTemplate(name="Minor Add 9", intervals=[0, 3, 7, 14])
SIXTH = ChordTemplate(name="6", intervals=[0, 4, 7, 9])
MINOR_SIXTH = ChordTemplate(name="m6", intervals=[0, 3, 7, 9])
SIXTY_NINE = ChordTemplate(name="6/9", intervals=[0, 4, 7, 9, 14])

CHORDS_DB: Dict[str, ChordTemplate] = {
    "maj": MAJOR_TRIAD,
    "min": MINOR_TRIAD,
    "dim": DIMINISHED_TRIAD,
    "aug": AUGMENTED_TRIAD,
    "maj7": MAJOR_7,
    "min7": MINOR_7,
    "dom7": DOMINANT_7,
    "m7b5": HALF_DIMINISHED_7,
    "dim7": DIMINISHED_7,
    "mmaj7": MINOR_MAJOR_7,
    "augmaj7": AUGMENTED_MAJOR_7,
    "aug7": AUGMENTED_7,
    "maj9": MAJOR_9,
    "min9": MINOR_9,
    "dom9": DOMINANT_9,
    "min11": MINOR_11,
    "dom11": DOMINANT_11,
    "sus2": SUS_2,
    "sus4": SUS_4,
    "add9": ADD_9,
    "madd9": MINOR_ADD_9,
    "6": SIXTH,
    "m6": MINOR_SIXTH,
    "6/9": SIXTY_NINE,
}

def get_chord(name: str) -> ChordTemplate:
    """Retrieve a chord template by symbol/name."""
    clean_name = name.lower()
    if clean_name not in CHORDS_DB:
        raise ValueError(f"Chord '{name}' not found.")
    return CHORDS_DB[clean_name]

def construct_chord_notes(root_midi: int, chord: ChordTemplate, inversion: int = 0) -> List[int]:
    """Constructs MIDI notes for a given root, chord type, and inversion."""
    notes = [root_midi + interval for interval in chord.intervals]
    
    # Handle inversions
    for _ in range(inversion % len(notes)):
        notes[0] += 12
        notes.sort()
        
    return notes
