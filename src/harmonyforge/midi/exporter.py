"""
MIDI Exporter V2.
Supports continuous timeline arrangement, separated stems, and arrangement metadata.
"""

import pretty_midi
import json
from typing import Dict, Any
from pathlib import Path
from harmonyforge.generation.arrangement_generator import Arrangement
from harmonyforge.midi.humanizer import humanize_instrument

def export_arrangement(arrangement: Arrangement, out_dir: Path) -> None:
    """
    Exports a hybrid package: continuous MIDI timeline, separated stems, and metadata.
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    
    bpm = arrangement.bpm
    beat_dur = 60.0 / bpm
    
    # Initialize global stems
    pm_chords = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst_chords = pretty_midi.Instrument(program=0, name="Chords")
    pm_chords.instruments.append(inst_chords)
    
    pm_bass = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst_bass = pretty_midi.Instrument(program=38, name="808 Bass")
    pm_bass.instruments.append(inst_bass)
    
    pm_melody = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst_melody = pretty_midi.Instrument(program=81, name="Lead Melody")
    pm_melody.instruments.append(inst_melody)
    
    # We also keep a combined PM
    pm_full = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    pm_full.instruments.extend([inst_chords, inst_bass, inst_melody])
    
    meta_json: Dict[str, Any] = {
        "bpm": bpm,
        "key": arrangement.key,
        "scale": arrangement.scale,
        "sections": []
    }
    
    # Render sections sequentially
    for section in arrangement.sections:
        start_time_sec = (section.start_bar * 4.0) * beat_dur
        
        meta_json["sections"].append({
            "name": section.name,
            "start_bar": section.start_bar,
            "length_bars": section.bars,
            "energy": section.energy,
            "active_instruments": section.active_instruments
        })
        
        # 1. Render Chords (looped over the section)
        if "chords" in section.active_instruments:
            bar_dur = beat_dur * 4.0
            loops = section.bars // 8
            if loops == 0:
                loops = 1  # fallback
            
            for loop_idx in range(loops):
                offset_time = start_time_sec + (loop_idx * 8 * bar_dur)
                current_time = offset_time
                for chord in section.progression.chords_midi:
                    for note in chord:
                        vel = int(100 * section.energy)
                        midi_note = pretty_midi.Note(
                            velocity=min(127, vel), pitch=note, start=current_time, end=current_time + bar_dur - 0.05
                        )
                        inst_chords.notes.append(midi_note)
                    current_time += bar_dur
                    
        # 2. Render Bass
        if "bass" in section.active_instruments:
            for b_event in section.bass:
                st = start_time_sec + (b_event.start_beat * beat_dur)
                et = st + (b_event.duration_beats * beat_dur)
                note = pretty_midi.Note(velocity=b_event.velocity, pitch=b_event.midi_note, start=st, end=et)
                inst_bass.notes.append(note)
                
                if b_event.pitch_bend != 0:
                    bend = pretty_midi.PitchBend(pitch=b_event.pitch_bend, time=st + (0.2 * beat_dur))
                    inst_bass.pitch_bends.append(bend)
                    inst_bass.pitch_bends.append(pretty_midi.PitchBend(pitch=0, time=et))
                    
        # 3. Render Melody
        if "melody" in section.active_instruments:
            for m_event in section.melody:
                st = start_time_sec + (m_event.start_beat * beat_dur)
                et = st + (m_event.duration_beats * beat_dur)
                note = pretty_midi.Note(velocity=m_event.velocity, pitch=m_event.midi_note, start=st, end=et)
                inst_melody.notes.append(note)
                
    # Humanize
    humanize_instrument(inst_chords)
    humanize_instrument(inst_melody)
    
    # Save files
    pm_full.write(str(out_dir / "full_arrangement.mid"))
    pm_chords.write(str(out_dir / "stem_chords.mid"))
    pm_bass.write(str(out_dir / "stem_bass.mid"))
    pm_melody.write(str(out_dir / "stem_melody.mid"))
    
    with open(out_dir / "arrangement.json", "w") as f:
        json.dump(meta_json, f, indent=4)
