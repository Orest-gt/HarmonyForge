"""
Generate Nick Mira-style beat for OREST_PRODUCTIONS.

Based on TEMPLATE_GENERATE_BEAT.py - following strict API patterns.
Nick Mira style: Dark melodic trap, emotional piano, heavy 808s, cinematic atmosphere.
"""

from pathlib import Path
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.midi.exporter import export_loop
from harmonyforge.styles.producers import NICK_MIRA
import logging

# Musical parameters (strictly following template)
PRODUCER = NICK_MIRA
BPM = 138
KEY_ROOT = "D"
SCALE_NAME = "Harmonic Minor"
BARS = 8
OUTPUT_FOLDER = "OREST_PRODUCTIONS"
SWING_STYLE = "trap_bounce"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_nick_mira_beat():
    """Generate a Nick Mira-style beat with DAW-ready stems."""
    
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
    try:
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
    except Exception as e:
        logger.error(f"Export failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    
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
    result = generate_nick_mira_beat()
    print(f"\n{'='*60}")
    print(f"BEAT GENERATION COMPLETE")
    print(f"{'='*60}")
    for key, value in result.items():
        print(f"{key:15}: {value}")
    print(f"{'='*60}")