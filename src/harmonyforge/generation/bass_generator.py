"""
808 Bass generator.
Creates syncopated patterns, octave jumps, and standard MIDI pitch bends for slides.
"""

import random
from typing import List
from pydantic import BaseModel

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature

class BassEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int
    pitch_bend: int = 0 # 0 means no bend, ranges from -8192 to 8191

def generate_808_pattern(progression_midi: List[List[int]], style: StyleSignature, bpm: int) -> List[BassEvent]:
    """
    Generates a trap-style 808 pattern based on the progression roots.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()
        
    events = []
    
    # Simple generation: 1 bar per chord (4 beats)
    for i, chord in enumerate(progression_midi):
        root = chord[0]
        # Ensure it's in the bass range (C1-C3 roughly)
        while root > 48:
            root -= 12
        while root < 24:
            root += 12
            
        current_beat = i * 4.0
        
        # Beat 1: Always hit the root
        velocity = rng.randint(100, 127)
        events.append(BassEvent(midi_note=root, start_beat=current_beat, duration_beats=1.0, velocity=velocity))
        
        # Decide if we add syncopated hits or octave jumps
        if rng.random() < style.syncopation_level:
            # Syncopated hit on the 'and' of 2 or 3
            sync_beat = current_beat + rng.choice([1.5, 2.5, 3.5])
            jump = rng.choice([0, 12]) if rng.random() > 0.5 else 0
            vel = rng.randint(80, 110)
            
            # Decide if this is a slide (pitch bend)
            bend = 0
            if rng.random() < 0.3: # 30% chance to pitch bend up a fifth or octave
                bend = rng.choice([8191]) # Max bend up
                
            events.append(BassEvent(
                midi_note=root + jump,
                start_beat=sync_beat,
                duration_beats=0.5,
                velocity=vel,
                pitch_bend=bend
            ))
            
    return events
