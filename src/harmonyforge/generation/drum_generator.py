"""
Drum generator v1.0 — Ultra simple, no random state issues.
"""

from typing import List
from pydantic import BaseModel

from harmonyforge.styles.genome import StyleSignature


class DrumEvent(BaseModel):
    midi_note: int  # General MIDI drum mapping
    start_beat: float
    duration_beats: float
    velocity: int


def generate_drum_pattern(
    style: StyleSignature,
    bpm: int,
    bars: int = 8
) -> List[DrumEvent]:
    """
    Generates drum patterns based on producer signature.
    
    GM Drum Mapping:
    36: Kick, 38: Snare, 40: Hi-hat closed, 42: Hi-hat open
    """
    events: List[DrumEvent] = []
    
    # Simple pattern for all bars - NO random state
    for bar in range(bars):
        bar_start = bar * 4.0
        
        # Kick on 1 and 3
        for kick_offset in [0.0, 2.0]:
            events.append(DrumEvent(
                midi_note=36,
                start_beat=bar_start + kick_offset,
                duration_beats=0.1,
                velocity=120
            ))
        
        # Snare on 2 and 4
        for snare_offset in [1.0, 3.0]:
            events.append(DrumEvent(
                midi_note=38,
                start_beat=bar_start + snare_offset,
                duration_beats=0.15,
                velocity=110
            ))
        
        # Hi-hats on 8th notes
        for i in range(8):
            hat_offset = i * 0.5
            events.append(DrumEvent(
                midi_note=40,
                start_beat=bar_start + hat_offset,
                duration_beats=0.05,
                velocity=100
            ))
    
    return events