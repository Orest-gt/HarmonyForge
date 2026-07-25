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
    fill_melody: Optional["List[MelodyEvent]"] = None,
    drums: Optional["List"] = None,
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

    # --- Fill Melody (Optional) ---
    if fill_melody:
        pm_fill = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
        inst_fill = pretty_midi.Instrument(program=89, name="Fill Melody")
        
        # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
        pm_fill.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
        )
        for f in fill_melody:
            st = _to_seconds(f.start_beat, bpm)
            et = st + (_to_seconds(f.duration_beats, bpm))
            inst_fill.notes.append(pretty_midi.Note(
                velocity=f.velocity, pitch=f.midi_note, start=st, end=et,
            ))
        if humanize:
            humanize_instrument(inst_fill, style_name=swing_style, bpm=bpm)
        pm_fill.instruments.append(inst_fill)
        pm_fill.write(str(out_dir / "stem_fill.mid"))

    # --- Drums (Optional) ---
    if drums:
        pm_drums = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
        inst_drums = pretty_midi.Instrument(program=0, name="Drums", is_drum=True)
        
        # Add TimeSignature (4/4) at time 0.0 for DAW compatibility
        pm_drums.time_signature_changes.append(
            pretty_midi.TimeSignature(numerator=4, denominator=4, time=0.0)
        )
        for d in drums:
            st = _to_seconds(d.start_beat, bpm)
            et = st + (_to_seconds(d.duration_beats, bpm))
            inst_drums.notes.append(pretty_midi.Note(
                velocity=d.velocity, pitch=d.midi_note, start=st, end=et,
            ))
        if humanize:
            humanize_instrument(inst_drums, style_name=swing_style, bpm=bpm)
        pm_drums.instruments.append(inst_drums)
        pm_drums.write(str(out_dir / "stem_drums.mid"))


def export_arrangement(arrangement: "Any", out_dir: Path) -> None:
    """Experimental arrangement export is not implemented in this version."""
    raise NotImplementedError(
        "export_arrangement is experimental and not implemented for this release."
    )
