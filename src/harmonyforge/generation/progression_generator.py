"""
Core deterministic generation engine for chord progressions based on Style Signatures.
"""

import random
from typing import List
from pydantic import BaseModel
import music21.pitch

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.harmony import get_diatonic_chords

class ProgressionResult(BaseModel):
    chords_midi: List[List[int]]
    chords_roman: List[str]
    scale_name: str
    key_root: str
    bpm: int

class ProgressionGenerator:
    def __init__(self, style: StyleSignature):
        self.style = style

    def generate(self, root_note: str, scale_name: str, bars: int = 8) -> ProgressionResult:
        """
        Generates a chord progression probabilistically guided by the style signature.
        Respects the global seed if configured.
        """
        # Ensure determinism based on config
        if config.seed is not None:
            rng = random.Random(config.seed)
        else:
            rng = random.Random()
            
        root_midi = music21.pitch.Pitch(f"{root_note}3").midi
        
        # Base diatonic chords (Triads by default, or 7ths if complexity > 0.6)
        chord_type = "7th" if self.style.harmonic_complexity > 0.6 else "triad"
        diatonic_pool = get_diatonic_chords(root_midi, scale_name, chord_type)
        
        # Roman numerals approximations for diatonic chords (simplified for structural purposes)
        # 1-indexed
        diatonic_roman = ["I", "ii", "iii", "IV", "V", "vi", "vii°"] if scale_name == "major" else ["i", "ii°", "III", "iv", "v", "VI", "VII"]
        
        progression = []
        roman = []
        
        # Simple markov-like or rule-based generation
        current_chord_idx = 0 # Start on tonic
        
        for i in range(bars):
            progression.append(diatonic_pool[current_chord_idx])
            roman.append(diatonic_roman[current_chord_idx])
            
            # Decide next chord based on rules
            if rng.random() < self.style.repetition_tendency and i > 0 and i % 2 != 0:
                # Repeat previous
                current_chord_idx = current_chord_idx
            else:
                # Move to another chord (simple heuristic)
                if current_chord_idx == 0:
                    choices = [3, 4, 5] # typical moves from I to IV, V, vi
                elif current_chord_idx in [3, 5]: # IV or vi
                    choices = [1, 4] # move to ii or V
                elif current_chord_idx == 4: # V
                    choices = [0, 5] # deceptive or authentic resolution
                else:
                    choices = [0, 3, 4] # default moves
                
                # Filter by list bounds
                choices = [c for c in choices if c < len(diatonic_pool)]
                if not choices:
                    choices = [0]
                    
                current_chord_idx = rng.choice(choices)
                
        # Generate a bpm based on style preferred range
        bpm = rng.randint(self.style.preferred_bpm_range[0], self.style.preferred_bpm_range[1])
                
        return ProgressionResult(
            chords_midi=progression,
            chords_roman=roman,
            scale_name=scale_name,
            key_root=root_note,
            bpm=bpm
        )
