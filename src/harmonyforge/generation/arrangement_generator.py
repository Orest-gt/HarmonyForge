"""
Phase 9: Arrangement Engine.
Structures generated progressions and melodies into full songs with energy curves.
Integrates Motif Memory for thematic consistency.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
import random

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.generation.progression_generator import ProgressionGenerator, ProgressionResult
from harmonyforge.generation.melody_generator import generate_melody, MelodyEvent
from harmonyforge.generation.bass_generator import generate_808_pattern, BassEvent

class SongSection(BaseModel):
    name: str
    start_bar: int
    bars: int
    energy: float # 0.0 to 1.0
    active_instruments: List[str] # e.g. ["chords", "bass", "melody"]
    progression: ProgressionResult
    melody: List[MelodyEvent]
    bass: List[BassEvent]

class Arrangement(BaseModel):
    sections: List[SongSection]
    bpm: int
    key: str
    scale: str

class MotifMemory:
    """Stores generated thematic material for reuse across sections."""
    def __init__(self) -> None:
        self.themes: Dict[str, List[MelodyEvent]] = {}
        
    def save_theme(self, name: str, events: List[MelodyEvent]) -> None:
        self.themes[name] = events
        
    def get_theme(self, name: str) -> Optional[List[MelodyEvent]]:
        return self.themes.get(name)

def generate_arrangement(key: str, scale: str, style: StyleSignature, total_bars: int = 64) -> Arrangement:
    """
    Generates a full song arrangement structure with automation curves and motif memory.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()
        
    # Standard Trap/Pop Structure mapping (Bars -> Section, Energy, Instruments)
    structure_template = [
        ("Intro", 8, 0.3, ["chords"]),
        ("Verse 1", 16, 0.5, ["chords", "bass"]),
        ("Hook 1", 16, 0.9, ["chords", "bass", "melody"]),
        ("Breakdown", 8, 0.2, ["chords", "melody"]),
        ("Hook 2", 16, 1.0, ["chords", "bass", "melody"])
    ]
    
    prog_gen = ProgressionGenerator(style)
    # Generate the master progression for the Hook (high energy)
    master_prog = prog_gen.generate(key, scale, 8) # 8-bar loop
    
    # Generate the master melody (the Hook motif)
    master_melody = generate_melody(master_prog.chords_midi, scale, key, style, master_prog.bpm)
    
    # Generate the master bassline
    master_bass = generate_808_pattern(master_prog.chords_midi, style, master_prog.bpm)
    
    motif_memory = MotifMemory()
    motif_memory.save_theme("hook_melody", master_melody)
    
    sections = []
    current_bar = 0
    
    for sec_name, sec_bars, energy, instruments in structure_template:
        if current_bar >= total_bars:
            break
            
        # Adjust section length if it exceeds total_bars
        actual_bars = min(sec_bars, total_bars - current_bar)
        
        # Depending on energy, we might simplify the progression or melody
        # For a true implementation, we would generate a new variation.
        # Here we reuse the 8-bar master loop, repeated to fill actual_bars
        
        # Expand loops to fit actual_bars (in chunks of 8)
        loops_needed = actual_bars // 8
        
        # Clone events and shift their start times
        sec_melody = []
        sec_bass = []
        
        if "melody" in instruments:
            # Re-use hook melody or generate verse melody based on energy
            if energy >= 0.8:
                base_mel = motif_memory.get_theme("hook_melody") or master_melody
            else:
                # Generate a sparser verse melody
                base_mel = generate_melody(master_prog.chords_midi, scale, key, style, master_prog.bpm)
                # Keep it sparse by randomly dropping notes
                base_mel = [m for m in base_mel if rng.random() > 0.4]
                
            for loop_i in range(loops_needed):
                bar_offset = loop_i * 8
                beat_offset = bar_offset * 4.0
                for m in base_mel:
                    # Adjust velocity based on energy curve
                    vel = int(m.velocity * energy)
                    sec_melody.append(MelodyEvent(
                        midi_note=m.midi_note, start_beat=m.start_beat + beat_offset,
                        duration_beats=m.duration_beats, velocity=vel
                    ))
                    
        if "bass" in instruments:
            for loop_i in range(loops_needed):
                bar_offset = loop_i * 8
                beat_offset = bar_offset * 4.0
                for b in master_bass:
                    vel = int(b.velocity * energy * 1.2) # Bass is usually louder
                    sec_bass.append(BassEvent(
                        midi_note=b.midi_note, start_beat=b.start_beat + beat_offset,
                        duration_beats=b.duration_beats, velocity=min(127, vel), pitch_bend=b.pitch_bend
                    ))
                    
        # Progression loop expansion handled inherently by the exporter later, 
        # but we pass the master_prog to know the chords.
        
        sections.append(SongSection(
            name=sec_name,
            start_bar=current_bar,
            bars=actual_bars,
            energy=energy,
            active_instruments=instruments,
            progression=master_prog,
            melody=sec_melody,
            bass=sec_bass
        ))
        
        current_bar += actual_bars
        
    return Arrangement(sections=sections, bpm=master_prog.bpm, key=key, scale=scale)
