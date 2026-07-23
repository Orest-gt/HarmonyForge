"""
808 Bass generator.
Creates syncopated patterns, octave jumps, flexible bass anchoring, and standard MIDI pitch bends for slides.
"""

import random
from typing import List, Optional
from pydantic import BaseModel

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature

class BassEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int
    pitch_bend: int = 0  # 0 means no bend, ranges from -8192 to 8191

def generate_808_pattern(progression_midi: List[List[int]], style: StyleSignature, bpm: int) -> List[BassEvent]:
    """
    Generates a trap-style 808 pattern based on progression roots and chord tones.
    Features flexible root_anchor_prob, pedal point persistence, and octave jumps.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()
        
    events: List[BassEvent] = []
    prev_bass_pitch: Optional[int] = None
    
    for i, chord in enumerate(progression_midi):
        # Transpose chord tones to bass register (C1 to C3 / 24 to 48)
        bass_candidates: List[int] = []
        for pitch in chord:
            p = pitch
            while p > 48:
                p -= 12
            while p < 24:
                p += 12
            bass_candidates.append(p)
            
        root_bass = bass_candidates[0]
        current_beat = i * 4.0
        
        # --- BEAT 1 BASS ANCHOR / PEDAL LOGIC ---
        if prev_bass_pitch is not None and rng.random() > style.root_anchor_prob and rng.random() < style.repetition_tendency:
            # Pedal point persistence: keep previous bar's bass pitch
            beat1_pitch = prev_bass_pitch
        elif rng.random() <= style.root_anchor_prob:
            # Default to Root note
            beat1_pitch = root_bass
        else:
            # Inversion / 3rd or 5th bass choice
            beat1_pitch = rng.choice(bass_candidates)

        prev_bass_pitch = beat1_pitch

        velocity = rng.randint(100, 127)
        events.append(BassEvent(
            midi_note=beat1_pitch,
            start_beat=current_beat,
            duration_beats=1.0,
            velocity=velocity
        ))
        
        # --- SYNCOPATION & SLIDE LOGIC ---
        if rng.random() < style.syncopation_level:
            sync_beat = current_beat + rng.choice([1.5, 2.5, 3.5])
            
            # Octave jump vs chord tone inversion
            if rng.random() < 0.45:
                # Stylistic octave jump
                sync_pitch = beat1_pitch + 12 if (beat1_pitch + 12) <= 54 else beat1_pitch
            else:
                sync_pitch = rng.choice(bass_candidates)
                
            bend = 0
            if rng.random() < (0.2 + 0.3 * style.syncopation_level):
                # Pitch bend slide (8191 = max bend up)
                bend = 8191
                
            vel = rng.randint(85, 115)
            events.append(BassEvent(
                midi_note=sync_pitch,
                start_beat=sync_beat,
                duration_beats=0.5,
                velocity=vel,
                pitch_bend=bend
            ))
            
    return events
