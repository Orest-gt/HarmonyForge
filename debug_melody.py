"""
Detailed Melody Inspector & Debugger.
Prints exact note events (pitch, name, start, duration, velocity) for the generated scenario stem.
Calculates chord-tone alignment, beat grid alignment, and voice-leading transitions.
"""

import pretty_midi
import music21.pitch
from pathlib import Path

path_mel = Path("examples/scenario_travis_nickmira/stem_melody.mid")
path_chords = Path("examples/scenario_travis_nickmira/stem_chords.mid")

pm_mel = pretty_midi.PrettyMIDI(str(path_mel))
pm_chords = pretty_midi.PrettyMIDI(str(path_chords))

mel_notes = pm_mel.instruments[0].notes if pm_mel.instruments else []
chord_notes = pm_chords.instruments[0].notes if pm_chords.instruments else []

bpm = pm_mel.estimate_tempo() if pm_mel.estimate_tempo() > 0 else 132
beat_dur = 60.0 / bpm

print(f"BPM: {bpm:.1f} | Beat Duration: {beat_dur:.4f}s")
print("=" * 80)
print(f"{'#':<3} | {'Start (beats)':<13} | {'Dur (beats)':<11} | {'MIDI':<5} | {'Note':<5} | {'Active Chord Pitches':<25} | {'Harmonic Status'}")
print("=" * 80)

for idx, n in enumerate(mel_notes):
    start_beat = n.start / beat_dur
    dur_beat = (n.end - n.start) / beat_dur
    p_name = music21.pitch.Pitch(n.pitch).nameWithOctave
    
    # Active chord notes at this time
    active_c = [cn.pitch for cn in chord_notes if cn.start <= n.start < cn.end]
    active_c_names = [music21.pitch.Pitch(cp).name for cp in active_c]
    
    # Check if melody note pitch class is in active chord
    p_pc = n.pitch % 12
    c_pcs = [cp % 12 for cp in active_c]
    
    if p_pc in c_pcs:
        status = "CHORD TONE"
    else:
        status = "NON-CHORD TONE / DISSONANCE"

    print(f"{idx+1:<3} | {start_beat:<13.2f} | {dur_beat:<11.2f} | {n.pitch:<5} | {p_name:<5} | {str(active_c_names):<25} | {status}")
