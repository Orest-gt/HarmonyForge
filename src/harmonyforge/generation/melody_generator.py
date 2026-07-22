"""
Melody generator.
Uses motifs and call-and-response mechanics.
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

def generate_melody(progression_midi: List[List[int]], scale_name: str, key_root: str, style: StyleSignature, bpm: int) -> List[MelodyEvent]:
    """
    Generates a lead melody based on the underlying progression and scale.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()
        
    events = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi
    
    scale = get_scale(scale_name)
    scale_notes = get_notes_in_scale(root_midi, scale, octaves=2)
    
    # Motif generation: create a short 1-bar rhythmic/melodic idea
    motif_rhythm = []
    beats_left = 4.0
    while beats_left > 0:
        dur = rng.choice([0.25, 0.5, 1.0])
        if dur > beats_left:
            dur = beats_left
        motif_rhythm.append(dur)
        beats_left -= dur
        
    # Generate notes for the full progression
    for i, chord in enumerate(progression_midi):
        current_beat = i * 4.0
        
        # Decide if this bar plays the motif, varies it, or rests (call and response)
        action = rng.choices(["motif", "variation", "rest"], weights=[0.5, 0.3, 0.2])[0]
        
        if action == "rest":
            continue
            
        for dur in motif_rhythm:
            # Pick a note. Bias towards chord tones on strong beats.
            if rng.random() > 0.3:
                # Chord tone (moved to melody range)
                base = rng.choice(chord)
                while base < 60:
                    base += 12
                note = base
            else:
                # Passing tone from scale
                note = rng.choice(scale_notes)
                
            if action == "variation" and rng.random() > 0.5:
                note = rng.choice(scale_notes)
                
            vel = rng.randint(70, 110)
            events.append(MelodyEvent(midi_note=note, start_beat=current_beat, duration_beats=dur*0.9, velocity=vel))
            current_beat += dur
            
    return events
