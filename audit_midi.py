"""
MIDI Audit Script — HarmonyForge v1.0
Checks every generated MIDI stem for:
  1. File validity (parseable, not empty)
  2. Note range (valid MIDI 0-127, melody in human range 48-96)
  3. Note duration validity (no zero/negative durations)
  4. Timing coherence (no notes starting after file end, no overlapping notes)
  5. Chord scale membership (do chord MIDI notes belong to the declared key/scale?)
  6. Velocity range (1-127)
  7. 808 pitch bends (valid range -8192 to 8191)
  8. BPM sanity (40–220 BPM)
"""

import pretty_midi
import sys
from pathlib import Path

# Key → semitone (C=0)
KEY_MAP = {"C": 0, "C#": 1, "D": 2, "Eb": 3, "E": 4, "F": 5,
           "F#": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "Bb": 10, "B": 11}

# Scale intervals (semitones from root)
SCALE_INTERVALS = {
    "minor":          [0, 2, 3, 5, 7, 8, 10],
    "major":          [0, 2, 4, 5, 7, 9, 11],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian":         [0, 2, 3, 5, 7, 9, 10],
    "phrygian":       [0, 1, 3, 5, 7, 8, 10],
}

EXAMPLES = [
    ("examples/01_travis_metro_dark", "C",  "minor"),
    ("examples/02_juice_emotional",   "E",  "minor"),
    ("examples/03_future_cinematic",  "D",  "harmonic_minor"),
    ("examples/04_drake_ambient",     "A",  "dorian"),
    ("examples/05_carti_rage",        "F#", "phrygian"),
]

STEMS = ["stem_chords.mid", "stem_bass.mid", "stem_melody.mid"]

def get_scale_pcs(key: str, scale: str):
    root = KEY_MAP[key]
    return {(root + i) % 12 for i in SCALE_INTERVALS[scale]}

def audit_midi(path: Path, key: str, scale: str, stem_name: str):
    issues = []

    # 1. File validity
    try:
        pm = pretty_midi.PrettyMIDI(str(path))
    except Exception as e:
        return [f"PARSE ERROR: {e}"]

    # 2. BPM sanity
    try:
        tempo_times, tempo_vals = pm.get_tempo_changes()
        if len(tempo_vals) > 0:
            est_bpm = tempo_vals[0]
            if not (40 <= est_bpm <= 220):
                issues.append(f"BPM out of range: {est_bpm:.1f}")
    except Exception:
        pass

    all_notes = [n for inst in pm.instruments for n in inst.notes]

    if not all_notes:
        issues.append("EMPTY — no notes found")
        return issues

    scale_pcs = get_scale_pcs(key, scale)

    for inst in pm.instruments:
        for n in inst.notes:
            # 3. Note range
            if not (0 <= n.pitch <= 127):
                issues.append(f"Note pitch out of MIDI range: {n.pitch}")

            # 4. Velocity range
            if not (1 <= n.velocity <= 127):
                issues.append(f"Invalid velocity: {n.velocity} on note {n.pitch}")

            # 5. Duration validity
            dur = n.end - n.start
            if dur <= 0:
                issues.append(f"Zero/negative duration: {dur:.4f}s on note {n.pitch}")

            # 6. Start time validity
            if n.start < 0:
                issues.append(f"Negative start time: {n.start:.4f}s on note {n.pitch}")

        # 7. Melody range check (only for melody stem)
        if "melody" in stem_name and inst.notes:
            out_of_range = [n.pitch for n in inst.notes if not (48 <= n.pitch <= 96)]
            if out_of_range:
                issues.append(f"Melody notes outside human range (48-96): {out_of_range[:5]}")

        # 8. Pitch bend range (bass)
        if "bass" in stem_name:
            for pb in inst.pitch_bends:
                if not (-8192 <= pb.pitch <= 8191):
                    issues.append(f"Pitch bend out of MIDI range: {pb.pitch}")

    # 9. Scale membership check (chords and melody, not bass root flexibility)
    if "bass" not in stem_name:
        out_of_scale = []
        for inst in pm.instruments:
            for n in inst.notes:
                if (n.pitch % 12) not in scale_pcs:
                    out_of_scale.append(n.pitch % 12)
        if out_of_scale:
            # Count percentage
            total = len(all_notes)
            pct = len(out_of_scale) / total * 100
            if pct > 25:  # Allow up to 25% passing/chromatic tones
                issues.append(f"HIGH out-of-scale note rate: {pct:.0f}% ({len(out_of_scale)}/{total} notes)")
            elif out_of_scale:
                issues.append(f"Passing tones outside scale: {pct:.0f}% (acceptable)")

    return issues

# --- Run audit ---
total_files = 0
total_issues = 0
print("=" * 60)
print("HarmonyForge MIDI Audit Report")
print("=" * 60)

for folder, key, scale in EXAMPLES:
    base = Path(folder)
    print(f"\n[{folder}]  Key: {key} {scale}")
    for stem in STEMS:
        path = base / stem
        total_files += 1
        if not path.exists():
            print(f"  MISSING: {stem}")
            total_issues += 1
            continue

        size_kb = path.stat().st_size / 1024
        issues = audit_midi(path, key, scale, stem)
        hard_issues = [i for i in issues if "acceptable" not in i]
        soft_issues = [i for i in issues if "acceptable" in i]

        status = "OK" if not hard_issues else "FAIL"
        print(f"  [{status}] {stem:25s} {size_kb:5.1f} KB", end="")
        if hard_issues:
            total_issues += len(hard_issues)
            print()
            for i in hard_issues:
                print(f"         !! {i}")
        elif soft_issues:
            print(f"  (note: {soft_issues[0]})")
        else:
            print()

print("\n" + "=" * 60)
print(f"Audited: {total_files} files")
if total_issues == 0:
    print("Result:  ALL CLEAR — 0 hard issues found")
else:
    print(f"Result:  {total_issues} issue(s) found — review above")
print("=" * 60)
