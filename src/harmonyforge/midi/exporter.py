"""
MIDI Exporter v1.1.

export_loop  — core path: exports stem files for a single loop (chords, bass, melody, counter-melody, vocal).
export_arrangement — experimental path: full song timeline + JSON metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List, Optional

import pretty_midi

from harmonyforge.midi.humanizer import humanize_instrument


def _to_seconds(beat: float, bpm: int) -> float:
    return beat * (60.0 / bpm)

if TYPE_CHECKING:
    from harmonyforge.generation.progression_generator import ProgressionResult
    from harmonyforge.generation.melody_generator import MelodyEvent
    from harmonyforge.generation.bass_generator import BassEvent


def export_loop(
    progression: "ProgressionResult",
    melody: "List[MelodyEvent]",
    bass: "List[BassEvent]",
    out_dir: Path,
    bpm: int,
    counter_melody: Optional["List[MelodyEvent]"] = None,
    vocal_topline: Optional["List[MelodyEvent]"] = None,
    swing_style: str = "straight",
    humanize: bool = False,
) -> None:
    """
    Exports clean MIDI stems for a single loop:
      stem_chords.mid         — open-spread Drop-2 pro voicings with rhythmic re-striking
      stem_bass.mid           — 808 pattern with standard MIDI pitch bends
      stem_melody.mid         — lead melody with genre swing templates
      stem_counter_melody.mid — optional counter-melody stem
      stem_vocal_topline.mid  — optional singable vocal topline stem
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    beat_dur = 60.0 / bpm
    bar_dur  = beat_dur * 4.0
    grid_16th_dur = beat_dur / 4.0

    # --- Chords ---
    pm_chords  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_chord = pretty_midi.Instrument(program=0, name="Chords")
    
    # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
    # pretty_midi uses absolute seconds for time parameter
    pm_chords.time_signature_changes.append(
        pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
    )

    if hasattr(progression, "chord_events") and progression.chord_events:
        for ce in progression.chord_events:
            st = _to_seconds(ce.start_beat, bpm)
            et = st + (_to_seconds(ce.duration_beats, bpm))
            for pitch in ce.midi_notes:
                inst_chord.notes.append(pretty_midi.Note(
                    velocity=ce.velocity, pitch=pitch, start=st, end=et
                ))
    else:
        t = 0.0
        for chord in progression.chords_midi:
            for pitch in chord:
                inst_chord.notes.append(pretty_midi.Note(
                    velocity=90, pitch=pitch, start=t, end=t + bar_dur
                ))
            t += bar_dur

    # Chord pads get minimal swing (0.2) — they anchor the harmonic grid.
    # Full swing only goes on melodic stems to avoid "late chord stab" artifacts.
    if humanize:
        humanize_instrument(inst_chord, style_name=swing_style, bpm=bpm, swing_strength=0.2)
    pm_chords.instruments.append(inst_chord)
    pm_chords.write(str(out_dir / "stem_chords.mid"))

    # --- Bass ---
    pm_bass  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_bass = pretty_midi.Instrument(program=38, name="808 Bass")
    
    # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
    pm_bass.time_signature_changes.append(
        pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
    )
    for b in bass:
        st = _to_seconds(b.start_beat, bpm)
        et = st + (_to_seconds(b.duration_beats, bpm))
        inst_bass.notes.append(pretty_midi.Note(
            velocity=b.velocity, pitch=b.midi_note, start=st, end=et,
        ))
        if b.pitch_bend != 0:
            inst_bass.pitch_bends.append(
                pretty_midi.PitchBend(pitch=b.pitch_bend, time=st + 0.2 * beat_dur)
            )
            inst_bass.pitch_bends.append(
                pretty_midi.PitchBend(pitch=0, time=et)
            )
    pm_bass.instruments.append(inst_bass)
    pm_bass.write(str(out_dir / "stem_bass.mid"))

    # --- Lead Melody ---
    pm_mel   = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_mel = pretty_midi.Instrument(program=81, name="Lead Melody")
    
    # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
    pm_mel.time_signature_changes.append(
        pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
    )
    for m in melody:
        st = _to_seconds(m.start_beat, bpm)
        et = st + (_to_seconds(m.duration_beats, bpm))
        inst_mel.notes.append(pretty_midi.Note(
            velocity=m.velocity, pitch=m.midi_note, start=st, end=et,
        ))
    if humanize:
        humanize_instrument(inst_mel, style_name=swing_style, bpm=bpm)
    pm_mel.instruments.append(inst_mel)
    pm_mel.write(str(out_dir / "stem_melody.mid"))

    # --- Counter-Melody (Optional) ---
    if counter_melody:
        pm_counter = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
        inst_counter = pretty_midi.Instrument(program=82, name="Counter Melody")
        
        # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
        pm_counter.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
        )
        for cm in counter_melody:
            st = _to_seconds(cm.start_beat, bpm)
            et = st + (_to_seconds(cm.duration_beats, bpm))
            inst_counter.notes.append(pretty_midi.Note(
                velocity=cm.velocity, pitch=cm.midi_note, start=st, end=et,
            ))
        if humanize:
            humanize_instrument(inst_counter, style_name=swing_style, bpm=bpm)
        pm_counter.instruments.append(inst_counter)
        pm_counter.write(str(out_dir / "stem_counter_melody.mid"))

    # --- Vocal Topline (Optional) ---
    if vocal_topline:
        pm_vocal = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
        inst_vocal = pretty_midi.Instrument(program=53, name="Vocal Topline")
        
        # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
        pm_vocal.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
        )
        for v in vocal_topline:
            st = _to_seconds(v.start_beat, bpm)
            et = st + (_to_seconds(v.duration_beats, bpm))
            inst_vocal.notes.append(pretty_midi.Note(
                velocity=v.velocity, pitch=v.midi_note, start=st, end=et,
            ))
        if humanize:
            humanize_instrument(inst_vocal, style_name=swing_style, bpm=bpm)
        pm_vocal.instruments.append(inst_vocal)
        pm_vocal.write(str(out_dir / "stem_vocal_topline.mid"))


def export_arrangement(arrangement: "Any", out_dir: Path, humanize: bool = False) -> None:
    """
    Experimental full-song export used by `harmonyforge arrange`.
    Produces: full_arrangement.mid, stem_*.mid, arrangement.json
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    bpm      = arrangement.bpm
    beat_dur = 60.0 / bpm

    pm_chords  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_chord = pretty_midi.Instrument(program=0,  name="Chords")
    pm_bass    = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_bass  = pretty_midi.Instrument(program=38, name="808 Bass")
    pm_melody  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_mel   = pretty_midi.Instrument(program=81, name="Lead Melody")

    pm_full = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    pm_full.instruments.extend([inst_chord, inst_bass, inst_mel])
    
    # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
    for midi_obj in [pm_full, pm_chords, pm_bass, pm_mel]:
        midi_obj.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
        )

    meta_json: Dict[str, Any] = {
        "bpm": bpm,
        "key": arrangement.key,
        "scale": arrangement.scale,
        "sections": [],
    }

    for section in arrangement.sections:
        start_sec = (section.start_bar * 4.0) * beat_dur
        bar_dur   = beat_dur * 4.0

        meta_json["sections"].append({
            "name":               section.name,
            "start_bar":          section.start_bar,
            "length_bars":        section.bars,
            "energy":             section.energy,
            "active_instruments": section.active_instruments,
        })

        if "chords" in section.active_instruments:
            if hasattr(section.progression, "chord_events") and section.progression.chord_events:
                loops = max(1, section.bars // 8)
                for li in range(loops):
                    loop_offset = start_sec + (li * 8 * bar_dur)
                    for ce in section.progression.chord_events:
                        st = loop_offset + (ce.start_beat * beat_dur)
                        et = st + (ce.duration_beats * beat_dur)
                        for pitch in ce.midi_notes:
                            inst_chord.notes.append(pretty_midi.Note(
                                velocity=int(ce.velocity * section.energy),
                                pitch=pitch, start=st, end=et,
                            ))
            else:
                loops = max(1, section.bars // 8)
                for li in range(loops):
                    t = start_sec + li * 8 * bar_dur
                    for chord in section.progression.chords_midi:
                        for pitch in chord:
                            inst_chord.notes.append(pretty_midi.Note(
                                velocity=int(100 * section.energy),
                                pitch=pitch, start=t, end=t + bar_dur,
                            ))
                        t += bar_dur

        if "bass" in section.active_instruments:
            for b in section.bass:
                st = start_sec + (b.start_beat * beat_dur)
                et = st + (b.duration_beats * beat_dur)
                inst_bass.notes.append(pretty_midi.Note(
                    velocity=b.velocity, pitch=b.midi_note, start=st, end=et,
                ))
                if b.pitch_bend != 0:
                    inst_bass.pitch_bends.append(
                        pretty_midi.PitchBend(pitch=b.pitch_bend, time=st + 0.2 * beat_dur)
                    )
                    inst_bass.pitch_bends.append(
                        pretty_midi.PitchBend(pitch=0, time=et)
                    )

        if "melody" in section.active_instruments:
            for m in section.melody:
                st = start_sec + (m.start_beat * beat_dur)
                et = st + (m.duration_beats * beat_dur)
                inst_mel.notes.append(pretty_midi.Note(
                    velocity=m.velocity, pitch=m.midi_note, start=st, end=et,
                ))

    if humanize:
        humanize_instrument(inst_chord)
        humanize_instrument(inst_mel)

    pm_chords.instruments.append(inst_chord)
    pm_bass.instruments.append(inst_bass)
    pm_melody.instruments.append(inst_mel)
    
    # Add TimeSignature (4/4) and TempoChange at tick 0 for DAW compatibility
    for midi_obj in [pm_full, pm_chords, pm_bass, pm_mel]:
        midi_obj.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0)
        )

    pm_full.write(str(out_dir / "full_arrangement.mid"))
    pm_chords.write(str(out_dir / "stem_chords.mid"))
    pm_bass.write(str(out_dir / "stem_bass.mid"))
    pm_melody.write(str(out_dir / "stem_melody.mid"))

    with open(out_dir / "arrangement.json", "w") as f:
        json.dump(meta_json, f, indent=4)
