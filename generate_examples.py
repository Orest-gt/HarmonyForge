import sys; sys.path.insert(0, "src")
from harmonyforge.core.config import config
from harmonyforge.styles.producers import get_producer
from harmonyforge.styles.artists import get_artist
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.midi.exporter import export_loop
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# BEAT 1 — CLASSIC
# Travis x Metro | F# harmonic minor | 140 BPM | trap_bounce
# The formula that built half of modern rap.
# Harmonic minor = that raised 7th "Egyptian" tension.
# Metro's syncopated bounce pattern. Travis chromatic melody.
# ─────────────────────────────────────────────────────────────────────────────
config.set_seed(808)

prod1  = get_producer("metro_boomin").signature
art1   = get_artist("travis_scott").signature
style1 = prod1.interpolate(art1, weight=0.3, non_linear=True)

gen1   = ProgressionGenerator(style1)
prog1  = gen1.generate("F#", "harmonic_minor", bars=8)
prog1  = prog1.model_copy(update={"bpm": 140})

mel1   = generate_melody(prog1.chords_midi, "harmonic_minor", "F#", style1, prog1.bpm)
bass1  = generate_808_pattern(prog1.chords_midi, style1, prog1.bpm)
ctr1   = generate_counter_melody(mel1, prog1.chords_midi, "harmonic_minor", "F#", style1, prog1.bpm)

out1 = Path("./output/classic__travis_x_metro_Fsharp_harmonic")
export_loop(prog1, mel1, bass1, out1, prog1.bpm, counter_melody=ctr1, swing_style="trap_bounce")

avg1 = sum(b.duration_beats for b in bass1) / len(bass1)
chords1 = " - ".join(prog1.chords_roman)
print("[CLASSIC]  F# harmonic_minor  BPM=" + str(prog1.bpm))
print("           Chords: " + chords1)
print("           lead=" + str(len(mel1)) + " notes  bass=" + str(len(bass1)) + " hits (avg " + f"{avg1:.1f}" + " beats)  counter=" + str(len(ctr1)))
print("           -> " + str(out1.resolve()))
print()

# ─────────────────────────────────────────────────────────────────────────────
# BEAT 2 — UNEXPECTED
# Southside x Mike Dean | Eb dorian | 116 BPM | dilla_swing
#
# Why this is unexpected:
# Southside = pitch-black minimal (darkness=0.95, syncopation=0.9)
# Mike Dean = harmonically dense (complexity=0.9, modal_interchange=0.7)
# Dorian = the "bittersweet" mode — sits between minor & major.
#           Minor 3rd & 7th = darkness. Major 6th = soul.
#           Think: D'Angelo, Kendrick "FEEL.", Herbie Hancock.
# Dilla swing at 116 BPM = every note drags just behind the pocket.
#
# The collision: 808 Mafia rawness + Neo-Soul harmonic warmth.
# The 808 hits hard. The chords breathe. Nobody expects this.
# ─────────────────────────────────────────────────────────────────────────────
config.set_seed(1969)

prod2  = get_producer("southside").signature
mdean  = get_producer("mike_dean").signature
style2 = prod2.interpolate(mdean, weight=0.45, non_linear=True)

gen2   = ProgressionGenerator(style2)
prog2  = gen2.generate("Eb", "dorian", bars=12)
prog2  = prog2.model_copy(update={"bpm": 116})

mel2   = generate_melody(prog2.chords_midi, "dorian", "Eb", style2, prog2.bpm)
bass2  = generate_808_pattern(prog2.chords_midi, style2, prog2.bpm)
ctr2   = generate_counter_melody(mel2, prog2.chords_midi, "dorian", "Eb", style2, prog2.bpm)

out2 = Path("./output/unexpected__southside_x_mikedean_Eb_dorian_dilla")
export_loop(prog2, mel2, bass2, out2, prog2.bpm, counter_melody=ctr2, swing_style="dilla_swing")

avg2    = sum(b.duration_beats for b in bass2) / len(bass2)
chords2 = " - ".join(prog2.chords_roman)
print("[UNEXPECTED]  Eb dorian  BPM=" + str(prog2.bpm))
print("              Chords: " + chords2)
print("              lead=" + str(len(mel2)) + " notes  bass=" + str(len(bass2)) + " hits (avg " + f"{avg2:.1f}" + " beats)  counter=" + str(len(ctr2)))
print("              darkness=" + f"{style2.darkness_level:.2f}" + "  complexity=" + f"{style2.harmonic_complexity:.2f}" + "  syncopation=" + f"{style2.syncopation_level:.2f}")
print("              -> " + str(out2.resolve()))
print()
print("Both beats ready. Import into DAW.")
