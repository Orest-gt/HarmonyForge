"""
Deep Musicality & Aesthetics Analyzer for HarmonyForge.
Checks:
  1. Motif Repetition & Pattern Coherence (Hookness)
  2. Interval Distribution (Melodic Contour sanity)
  3. 808 Bass Root Lock & Rhythmic Pocket Placement
  4. Pitch Entropy & Style Signature Contrast
"""

import pretty_midi
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

EXAMPLES = [
    ("examples/01_travis_metro_dark", "Travis x Metro (Dark)"),
    ("examples/02_juice_emotional",   "Juice x Nick Mira (Emotional)"),
    ("examples/03_future_cinematic",  "Future x Metro (Cinematic)"),
    ("examples/04_drake_ambient",     "Drake x Mike Dean (Ambient)"),
    ("examples/05_carti_rage",        "Carti x Southside (Rage)"),
]

def analyze_melody_structure(pm_mel: pretty_midi.PrettyMIDI):
    notes = pm_mel.instruments[0].notes if pm_mel.instruments else []
    if not notes:
        return {}

    pitches = [n.pitch for n in notes]
    starts = [n.start for n in notes]
    durations = [n.end - n.start for n in notes]

    # 1. Interval distribution (semitones between consecutive notes)
    intervals = [abs(pitches[i+1] - pitches[i]) for i in range(len(pitches)-1)]
    repeated_pitches_pct = (intervals.count(0) / len(intervals) * 100) if intervals else 0
    stepwise_pct = (sum(1 for d in intervals if 1 <= d <= 3) / len(intervals) * 100) if intervals else 0
    leap_pct = (sum(1 for d in intervals if d > 7) / len(intervals) * 100) if intervals else 0

    # 2. Motif Self-Similarity (Bar 1-2 vs Bar 3-4 pitch pattern correlation)
    # Quantize notes to 16th grid ( assuming 4/4 )
    bpm = pm_mel.estimate_tempo() if pm_mel.estimate_tempo() > 0 else 140
    beat_dur = 60.0 / bpm
    grid_16th = beat_dur / 4.0

    # Create 32-step 16th grid for 2 bars
    grid_bar1_2 = np.zeros(32)
    grid_bar3_4 = np.zeros(32)

    for n in notes:
        step = int(round(n.start / grid_16th))
        if step < 32:
            grid_bar1_2[step] = n.pitch
        elif 32 <= step < 64:
            grid_bar3_4[step - 32] = n.pitch

    # Motif similarity (how much bar 3-4 repeats bar 1-2 pattern)
    active_steps = (grid_bar1_2 > 0) & (grid_bar3_4 > 0)
    if np.sum(active_steps) > 0:
        similarity = np.mean(grid_bar1_2[active_steps] == grid_bar3_4[active_steps]) * 100
    else:
        similarity = 0.0

    # 3. Pitch Entropy (Uniqueness vs Repetition)
    unique_pitches = len(set(pitches))

    return {
        "note_count": len(notes),
        "unique_pitches": unique_pitches,
        "repeated_notes_pct": repeated_pitches_pct,
        "stepwise_pct": stepwise_pct,
        "large_leaps_pct": leap_pct,
        "motif_repetition_pct": similarity,
    }

def analyze_bass_groove(pm_bass: pretty_midi.PrettyMIDI, pm_chords: pretty_midi.PrettyMIDI):
    bass_notes = pm_bass.instruments[0].notes if pm_bass.instruments else []
    chord_notes = pm_chords.instruments[0].notes if pm_chords.instruments else []

    if not bass_notes:
        return {}

    bpm = pm_bass.estimate_tempo() if pm_bass.estimate_tempo() > 0 else 140
    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0

    # 1. Check Downbeat Pocket (Does 808 hit bar 1 beat 1?)
    downbeat_hits = 0
    total_bars = max(1, int(round(pm_bass.get_end_time() / bar_dur)))

    for b in range(total_bars):
        bar_start = b * bar_dur
        # Check if there is an 808 note within 50ms of bar_start
        has_hit = any(abs(n.start - bar_start) < 0.08 for n in bass_notes)
        if has_hit:
            downbeat_hits += 1

    downbeat_pocket_pct = (downbeat_hits / total_bars) * 100

    # 2. Harmonic Alignment with Chords (Is 808 root matching chord bass note?)
    harmonic_matches = 0
    for bn in bass_notes:
        # Find active chord at bass note start
        active_chords = [cn.pitch % 12 for cn in chord_notes if cn.start <= bn.start < cn.end]
        if active_chords:
            # Check if 808 pitch is in the active chord (ideally the root/lowest note)
            if (bn.pitch % 12) in active_chords:
                harmonic_matches += 1

    harmonic_lock_pct = (harmonic_matches / len(bass_notes) * 100) if bass_notes else 0

    return {
        "bass_notes_count": len(bass_notes),
        "downbeat_pocket_pct": downbeat_pocket_pct,
        "harmonic_lock_pct": harmonic_lock_pct,
        "pitch_bends_count": len(pm_bass.instruments[0].pitch_bends) if pm_bass.instruments else 0
    }

print("=" * 75)
print("HARMONYFORGE MUSICALITY & GROOVE AUDIT REPORT")
print("=" * 75)

for folder, label in EXAMPLES:
    path_mel = Path(folder) / "stem_melody.mid"
    path_bass = Path(folder) / "stem_bass.mid"
    path_chords = Path(folder) / "stem_chords.mid"

    pm_mel = pretty_midi.PrettyMIDI(str(path_mel))
    pm_bass = pretty_midi.PrettyMIDI(str(path_bass))
    pm_chords = pretty_midi.PrettyMIDI(str(path_chords))

    mel_stats = analyze_melody_structure(pm_mel)
    bass_stats = analyze_bass_groove(pm_bass, pm_chords)

    print(f"\n[{label}]")
    print("   +-- MELODY CONTOUR & MOTIF:")
    print(f"   |  +-- Total Notes: {mel_stats['note_count']} (Unique Pitches: {mel_stats['unique_pitches']})")
    print(f"   |  +-- Repeated Pitch Rate (Pedal): {mel_stats['repeated_notes_pct']:.1f}%")
    print(f"   |  +-- Stepwise Motion (1-3 semitones): {mel_stats['stepwise_pct']:.1f}%")
    print(f"   |  +-- Large Unmusical Leaps (>7 semitones): {mel_stats['large_leaps_pct']:.1f}%")
    print(f"   |  +-- Motif Repetition (Bar 1-2 -> Bar 3-4): {mel_stats['motif_repetition_pct']:.1f}%")
    print("   +-- 808 BASS GROOVE & HARMONY:")
    print(f"      +-- Downbeat Pocket Hit Rate: {bass_stats['downbeat_pocket_pct']:.1f}%")
    print(f"      +-- Harmonic Lock with Chords: {bass_stats['harmonic_lock_pct']:.1f}%")
    print(f"      +-- 808 Pitch Bend Slides: {bass_stats['pitch_bends_count']} events")

print("\n" + "=" * 75)
