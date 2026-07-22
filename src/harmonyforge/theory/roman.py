"""
Roman numeral parsing and evaluation.
Leverages music21 for robust Roman numeral parsing and translates to our engine format.
"""

from typing import List, Tuple
import music21.roman
import music21.key
import music21.pitch

def parse_roman_numeral(numeral: str, key_str: str) -> Tuple[List[str], List[int]]:
    """
    Parses a Roman numeral in a specific key.
    
    Args:
        numeral: e.g., 'V7', 'ii', 'Imaj7', 'V/V'
        key_str: e.g., 'C', 'A minor', 'F# major'
        
    Returns:
        Tuple of (List of note names, List of MIDI pitches)
    """
    try:
        key_obj = music21.key.Key(key_str)
        rn = music21.roman.RomanNumeral(numeral, key_obj)
        
        note_names = [p.nameWithOctave for p in rn.pitches]
        midi_pitches = [p.midi for p in rn.pitches]
        
        return note_names, midi_pitches
    except Exception as e:
        raise ValueError(f"Failed to parse Roman numeral '{numeral}' in key '{key_str}': {str(e)}")

def get_diatonic_progression(numerals: List[str], key_str: str) -> List[List[int]]:
    """
    Convert a list of Roman numerals into a progression of MIDI pitches.
    """
    progression = []
    for num in numerals:
        _, pitches = parse_roman_numeral(num, key_str)
        progression.append(pitches)
    return progression
