"""
MIDI Exporter v1.0.

export_loop  — core v1.0 path: exports 3 stem files for a single loop.
export_arrangement — experimental path: full song timeline + JSON metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List

import pretty_midi

from harmonyforge.midi.humanizer import humanize_instrument

if TYPE_CHECKING:
    from harmonyforge.generation.progression_generator import ProgressionResult
    from harmonyforge.generation.melody_generator import MelodyEvent
    from harmonyforge.generation.bass_generator import BassEvent


# ---------------------------------------------------------------------------
# v1.0 core: single-loop export
# ---------------------------------------------------------------------------

def export_loop(
    progression: "ProgressionResult",
    melody: "List[MelodyEvent]",
    bass: "List[BassEvent]",
    out_dir: Path,
    bpm: int,
) -> None:
    """
    Exports three clean MIDI stems for a single loop:
      stem_chords.mid  — chord pads, one note-per-bar per pitch
      stem_bass.mid    — 808 pattern with standard MIDI pitch bends
      stem_melody.mid  — lead melody with humanization

    All files land in out_dir and are immediately drag-ready for any DAW.
    """
    out_dir.mkdir(exist_ok=True, parents=True)
    beat_dur = 60.0 / bpm
    bar_dur  = beat_dur * 4.0

    # --- Chords ---
    pm_chords  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_chord = pretty_midi.Instrument(program=0, name="Chords")
    t = 0.0
    for chord in progression.chords_midi:
        for pitch in chord:
            inst_chord.notes.append(pretty_midi.Note(
                velocity=90, pitch=pitch,
                start=t, end=t + bar_dur,
            ))
        t += bar_dur
    humanize_instrument(inst_chord)
    pm_chords.instruments.append(inst_chord)
    pm_chords.write(str(out_dir / "stem_chords.mid"))

    # --- Bass ---
    pm_bass  = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_bass = pretty_midi.Instrument(program=38, name="808 Bass")
    for b in bass:
        st = b.start_beat    * beat_dur
        et = st + b.duration_beats * beat_dur
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

    # --- Melody ---
    pm_mel   = pretty_midi.PrettyMIDI(initial_tempo=float(bpm))
    inst_mel = pretty_midi.Instrument(program=81, name="Lead Melody")
    for m in melody:
        st = m.start_beat    * beat_dur
        et = st + m.duration_beats * beat_dur
        inst_mel.notes.append(pretty_midi.Note(
            velocity=m.velocity, pitch=m.midi_note, start=st, end=et,
        ))
    humanize_instrument(inst_mel)
    pm_mel.instruments.append(inst_mel)
    pm_mel.write(str(out_dir / "stem_melody.mid"))


# ---------------------------------------------------------------------------
# Experimental: full-song arrangement export
# ---------------------------------------------------------------------------

def export_arrangement(arrangement: "Any", out_dir: Path) -> None:
    """
    Experimental full-song export used by `harmonyforge arrange`.
    Produces: full_arrangement.mid, stem_*.mid, arrangement.json
    """
    from harmonyforge.generation.arrangement_generator import Arrangement  # noqa: F401

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
            loops = max(1, section.bars // 8)
            for li in range(loops):
                t = start_sec + li * 8 * bar_dur
                for chord in section.progression.chords_midi:
                    for pitch in chord:
                        inst_chord.notes.append(pretty_midi.Note(
                            velocity=int(100 * section.energy),
                            pitch=pitch, start=t, end=t + bar_dur - 0.05,
                        ))
                    t += bar_dur

        if "bass" in section.active_instruments:
            for b in section.bass:
                st = start_sec + b.start_beat    * beat_dur
                et = st + b.duration_beats * beat_dur
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
                st = start_sec + m.start_beat    * beat_dur
                et = st + m.duration_beats * beat_dur
                inst_mel.notes.append(pretty_midi.Note(
                    velocity=m.velocity, pitch=m.midi_note, start=st, end=et,
                ))

    humanize_instrument(inst_chord)
    humanize_instrument(inst_mel)

    pm_chords.instruments.append(inst_chord)
    pm_bass.instruments.append(inst_bass)
    pm_melody.instruments.append(inst_mel)

    pm_full.write(str(out_dir / "full_arrangement.mid"))
    pm_chords.write(str(out_dir / "stem_chords.mid"))
    pm_bass.write(str(out_dir / "stem_bass.mid"))
    pm_melody.write(str(out_dir / "stem_melody.mid"))

    with open(out_dir / "arrangement.json", "w") as f:
        json.dump(meta_json, f, indent=4)
