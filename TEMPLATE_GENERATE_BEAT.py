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
from harmonyforge.core.config import config
from harmonyforge.generation.melody_generator import generate_melody, refine_melody_with_ai
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.generation.drum_generator import generate_drum_pattern
from harmonyforge.midi.exporter import export_loop
from harmonyforge.styles.producers import (
    NICK_MIRA, METRO_BOOMIN, SOUTHSIDE, TAY_KEITH,
    MIKE_DEAN, ATL_JACOB, FORTY, WHEEZY, BOI_1DA, HIT_BOY
)
import logging
import os

# ==============================================================================
# MUSICAL PARAMETERS - MODIFY ONLY THIS SECTION
# ==============================================================================

# Choose producer style from available producers
PRODUCER = NICK_MIRA  # Options: NICK_MIRA, METRO_BOOMIN, SOUTHSIDE, TAY_KEITH, etc.

# Musical parameters
BPM = 138
KEY_ROOT = "D"  # String format: "C", "D", "F#", "Bb", etc.
SCALE_NAME = "Harmonic Minor"  # String format: "Major", "Minor", "Harmonic Minor", "Phrygian", etc.
BARS = 4
OUTPUT_FOLDER = "OREST_PRODUCTIONS"  # Your output folder name
SWING_STYLE = "trap_bounce"  # Options: "straight", "trap_bounce", "dilla_swing", "drill_push", "afro_triplet"

# AI Configuration (optional)
ENABLE_AI_REFINEMENT = True  # Enable AI-powered melody refinement
AI_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for AI suggestions (0.0-1.0)

# ==============================================================================
# GENERATION ENGINE - DO NOT MODIFY BELOW THIS LINE
# ==============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_beat():
    """Generate a professional beat with DAW-ready stems."""
    
    # Force 8 bars regardless of config
    bars = 8
    
    # Set random seed for variety between generations
    import random
    import time
    seed = int(time.time() * 1000) % 10000
    config.set_seed(seed)
    
    logger.info(f"Generating {PRODUCER.name} beat: {KEY_ROOT} {SCALE_NAME}, {BPM} BPM, {bars} bars (seed: {seed})")
    logger.debug(f"Producer: {PRODUCER}")
    logger.debug(f"Parameters: BPM={BPM}, KEY={KEY_ROOT}, SCALE={SCALE_NAME}, BARS={bars}")
    
    # Store seed for return value
    generation_seed = seed
    
    # Generate progression (CRITICAL: use .signature attribute)
    logger.debug("Creating ProgressionGenerator...")
    prog_gen = ProgressionGenerator(style=PRODUCER.signature)
    logger.debug("Generating progression...")
    progression = prog_gen.generate(root_note=KEY_ROOT, scale_name=SCALE_NAME, bars=bars)
    logger.info(f"Generated progression: {progression.chords_roman}")
    
    # Generate melody (CRITICAL: correct parameter order)
    logger.debug("Generating melody...")
    melody = generate_melody(
        progression_midi=progression.chords_midi,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated melody with {len(melody)} notes")
    
    # Optional: Apply AI refinement if enabled
    ai_metadata = {}
    if ENABLE_AI_REFINEMENT:
        logger.debug("Applying AI refinement...")
        try:
            melody, ai_metadata = refine_melody_with_ai(
                melody_events=melody,
                scale_name=SCALE_NAME,
                key_root=KEY_ROOT,
                style=PRODUCER.signature,
                enable_ai=True,
                ai_confidence_threshold=AI_CONFIDENCE_THRESHOLD
            )
            
            if ai_metadata['ai_used']:
                logger.info(f"AI refinement applied: {ai_metadata['applied_suggestions']}/{ai_metadata['total_suggestions']} suggestions")
                logger.info(f"AI cost: ${ai_metadata['cost_usd']:.6f} ({ai_metadata['input_tokens']} input + {ai_metadata['output_tokens']} output tokens)")
                if ai_metadata['was_mock']:
                    logger.info("AI mode: MOCK (no real API calls)")
                else:
                    logger.info("AI mode: REAL API")
            else:
                logger.info(f"AI refinement skipped: {ai_metadata['reason']}")
        except Exception as e:
            logger.warning(f"AI refinement failed: {e}. Using original melody.")
    
    # Generate bass (CRITICAL: only required parameters)
    logger.debug("Generating bass...")
    bass = generate_808_pattern(
        progression_midi=progression.chords_midi,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated bass with {len(bass)} notes")
    
    # Generate counter melody (CRITICAL: lead_events as first parameter)
    logger.debug("Generating counter melody...")
    counter_melody = generate_counter_melody(
        lead_events=melody,
        progression_midi=progression.chords_midi,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        bpm=BPM
    )
    logger.info(f"Generated counter melody with {len(counter_melody)} notes")
    
    # Generate drums (NEW: Style-aware drum patterns)
    logger.debug("Generating drums...")
    drums = generate_drum_pattern(
        style=PRODUCER.signature,
        bpm=BPM,
        bars=bars
    )
    logger.info(f"Generated drums with {len(drums)} notes")
    
    # Export to folder (CRITICAL: TimeSignature uses time=0.0, not tick 0)
    output_dir = Path(OUTPUT_FOLDER)
    logger.debug(f"Output directory: {output_dir.absolute()}")
    logger.debug(f"Output directory exists: {output_dir.exists()}")
    try:
        logger.debug("Starting export...")
        export_loop(
            progression=progression,
            melody=melody,
            bass=bass,
            out_dir=output_dir,
            bpm=BPM,
            counter_melody=counter_melody,
            drums=drums,
            swing_style=SWING_STYLE
        )
        logger.debug("Export completed successfully")
        
        # Check if files were actually created
        logger.debug(f"Checking files in {output_dir.absolute()}")
        if output_dir.exists():
            files = list(output_dir.glob("*.mid"))
            logger.info(f"Found {len(files)} MIDI files in output directory")
            for f in files:
                logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")
        else:
            logger.error(f"Output directory {output_dir.absolute()} does not exist!")
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    logger.info(f"Beat exported to {output_dir}/")
    logger.info("Stems: stem_chords.mid, stem_melody.mid, stem_bass.mid, stem_counter_melody.mid")
    
    return {
        "producer": PRODUCER.name,
        "bpm": BPM,
        "key": KEY_ROOT,
        "scale": SCALE_NAME,
        "bars": bars,
        "output_dir": str(output_dir),
        "swing_style": SWING_STYLE,
        "seed": generation_seed,
        "progression": progression.chords_roman,
        "melody_notes": len(melody),
        "bass_notes": len(bass),
        "drum_notes": len(drums),
        "ai_refinement": ai_metadata
    }

if __name__ == "__main__":
    import sys
    
    # Check if running in batch mode
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Generate 10 beats for comparison
        print("BATCH GENERATION: 10 Nick Mira beats")
        print("=" * 60)
        
        results = []
        for i in range(10):
            result = generate_beat()
            results.append(result)
            print(f"Beat {i+1} complete (seed: {result['seed']}, melody: {result['melody_notes']} notes)")
        
        print("\n" + "=" * 60)
        print("COMPARISON SUMMARY")
        print("=" * 60)
        
        # Compare note counts
        note_counts = [r.get('melody_notes', 0) for r in results]
        avg_notes = sum(note_counts) / len(note_counts) if note_counts else 0
        print(f"Average melody notes: {avg_notes:.1f}")
        print(f"Note count range: {min(note_counts)}-{max(note_counts)}")
        
        # Compare bass notes
        bass_counts = [r.get('bass_notes', 0) for r in results]
        avg_bass = sum(bass_counts) / len(bass_counts) if bass_counts else 0
        print(f"Average bass notes: {avg_bass:.1f}")
        print(f"Bass count range: {min(bass_counts)}-{max(bass_counts)}")
        
        # Compare drum notes
        drum_counts = [r.get('drum_notes', 0) for r in results]
        avg_drums = sum(drum_counts) / len(drum_counts) if drum_counts else 0
        print(f"Average drum notes: {avg_drums:.1f}")
        print(f"Drum count range: {min(drum_counts)}-{max(drum_counts)}")
        
        # Compare seeds
        seeds = [r['seed'] for r in results]
        print(f"Seed range: {min(seeds)}-{max(seeds)}")
        print(f"All unique seeds: {len(set(seeds)) == 10}")
        
        # Calculate variety score
        melody_variety = len(set(note_counts))
        bass_variety = len(set(bass_counts))
        drum_variety = len(set(drum_counts))
        print(f"Variety score: {melody_variety + bass_variety + drum_variety}/30")
        
    else:
        # Single beat generation
        result = generate_beat()
        print(f"\n{'='*60}")
        print(f"BEAT GENERATION COMPLETE")
        print(f"{'='*60}")
        for key, value in result.items():
            print(f"{key:15}: {value}")
        print(f"{'='*60}")