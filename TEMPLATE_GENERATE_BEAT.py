"""
PROFESSIONAL BEAT GENERATION TEMPLATE

Strict pattern for generating producer beats with DAW-ready stems.
Follow this template exactly to avoid API errors and ensure consistency.

USAGE:
1. Copy this file to your beat name (e.g., generate_my_beat.py)
2. Modify only the MUSICAL PARAMETERS section
3. Run: python generate_my_beat.py

API PATTERNS (DO NOT CHANGE):
- ProgressionGenerator: ProgressionGenerator(style=PRODUCER.signature)
- generate_melody: generate_melody(progression_midi, scale_name, key_root, style, bpm)
- generate_808_pattern: generate_808_pattern(progression_midi, style, bpm)
- generate_counter_melody: generate_counter_melody(lead_events, progression_midi, scale_name, key_root, style, bpm)
- export_loop: export_loop(progression, melody, bass, out_dir, bpm, counter_melody, swing_style)

STRICT RULES:
- Always use .signature attribute from ProducerProfile
- Always use correct parameter names exactly as shown
- Always use string format for scale_name (e.g., "Harmonic Minor")
- Always use string format for key_root (e.g., "D")
- Always check actual function signatures before calling
"""

from pathlib import Path
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.midi.exporter import export_loop
from harmonyforge.styles.producers import (
    NICK_MIRA, METRO_BOOMIN, SOUTHSIDE, TAY_KEITH, PIERRE_BOURNE,
    MIKE_DEAN, MURDA_BEATZ, ATL_JACOB, RONNY_J, FRANK_DUKES
)
import logging

# ==============================================================================
# MUSICAL PARAMETERS - MODIFY ONLY THIS SECTION
# ==============================================================================

# Choose producer style from available producers
PRODUCER = NICK_MIRA  # Options: NICK_MIRA, METRO_BOOMIN, SOUTHSIDE, TAY_KEITH, etc.

# Musical parameters
BPM = 138
KEY_ROOT = "D"  # String format: "C", "D", "F#", "Bb", etc.
SCALE_NAME = "Harmonic Minor"  # String format: "Major", "Minor", "Harmonic Minor", "Phrygian", etc.
BARS = 8
OUTPUT_FOLDER = "OREST_PRODUCTIONS"  # Your output folder name
SWING_STYLE = "trap_bounce"  # Options: "straight", "trap_bounce", "dilla_swing", "drill_push", "afro_triplet"

# ==============================================================================
# GENERATION ENGINE - DO NOT MODIFY BELOW THIS LINE
# ==============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_beat():
    """Generate a professional beat with DAW-ready stems."""
    
    logger.info(f"Generating {PRODUCER.name} beat: {KEY_ROOT} {SCALE_NAME}, {BPM} BPM, {BARS} bars")
    
    # Generate progression (CRITICAL: use .signature attribute)
    prog_gen = ProgressionGenerator(style=PRODUCER.signature)
    progression = prog_gen.generate(root_note=KEY_ROOT, scale_name=SCALE_NAME, bars=BARS)
    logger.info(f"Generated progression: {progression.chords_roman}")
    
    # Generate melody (CRITICAL: correct parameter order)
    melody = generate_melody(
        progression_midi=progression.chords_midi,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated melody with {len(melody)} notes")
    
    # Generate bass (CRITICAL: only required parameters)
    bass = generate_808_pattern(
        progression_midi=progression.chords_midi,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated bass with {len(bass)} notes")
    
    # Generate counter melody (CRITICAL: lead_events as first parameter)
    counter_melody = generate_counter_melody(
        lead_events=melody,
        progression_midi=progression.chords_midi,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated counter melody with {len(counter_melody)} notes")
    
    # Export to folder (CRITICAL: TimeSignature uses time=0.0, not tick 0)
    output_dir = Path(OUTPUT_FOLDER)
    export_loop(
        progression=progression,
        melody=melody,
        bass=bass,
        out_dir=output_dir,
        bpm=BPM,
        counter_melody=counter_melody,
        swing_style=SWING_STYLE
    )
    
    logger.info(f"Beat exported to {output_dir}/")
    logger.info("Stems: stem_chords.mid, stem_melody.mid, stem_bass.mid, stem_counter_melody.mid")
    
    return {
        "producer": PRODUCER.name,
        "bpm": BPM,
        "key": KEY_ROOT,
        "scale": SCALE_NAME,
        "bars": BARS,
        "output_dir": str(output_dir),
        "swing_style": SWING_STYLE
    }

if __name__ == "__main__":
    result = generate_beat()
    print(f"\n{'='*60}")
    print(f"BEAT GENERATION COMPLETE")
    print(f"{'='*60}")
    for key, value in result.items():
        print(f"{key:15}: {value}")
    print(f"{'='*60}")