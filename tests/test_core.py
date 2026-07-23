"""
Unit tests for HarmonyForge V2.1.
Covers: genome interpolation, evaluation engine, arrangement generation,
NLP parser, and MIDI export round-trip.
"""

import copy
import random

import pretty_midi
from typer.testing import CliRunner

from harmonyforge.styles.genome import StyleSignature
from harmonyforge.generation.melody_generator import select_weighted_pitch
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.midi.humanizer import humanize_instrument
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature, extract_structured_params
from harmonyforge.analysis.evaluation import evaluate_progression, calculate_originality
from harmonyforge.generation.arrangement_generator import generate_arrangement
from harmonyforge.cli.main import app, main

runner = CliRunner()


def test_expanded_profile_database_contains_real_world_signatures():
    """The database should expose richer artist/producer profiles beyond the original trap-centric set."""
    drake = get_artist("Drake")
    kendrick = get_artist("Kendrick Lamar")
    forty = get_producer("40")
    wheezy = get_producer("Wheezy")

    assert drake.name == "Drake"
    assert kendrick.name == "Kendrick Lamar"
    assert forty.name == "40"
    assert wheezy.name == "Wheezy"
    assert drake.signature.darkness_level < 0.7
    assert kendrick.signature.harmonic_complexity > 0.6
    assert forty.signature.rhythmic_density < 0.6
    assert wheezy.signature.syncopation_level > 0.7


# --- Genome Interpolation Tests ---

def test_linear_interpolation_midpoint():
    """Blending at weight=0.5 (linear) should give the exact average."""
    a = StyleSignature(harmonic_complexity=0.0, darkness_level=0.0)
    b = StyleSignature(harmonic_complexity=1.0, darkness_level=1.0)
    blended = a.interpolate(b, weight=0.5, non_linear=False)
    assert abs(blended.harmonic_complexity - 0.5) < 0.01
    assert abs(blended.darkness_level - 0.5) < 0.01


def test_nonlinear_interpolation_boundaries():
    """Non-linear blend at weight=0.0 should be almost fully `self`."""
    a = StyleSignature(harmonic_complexity=0.1, darkness_level=0.1)
    b = StyleSignature(harmonic_complexity=0.9, darkness_level=0.9)
    blended = a.interpolate(b, weight=0.01, non_linear=True)
    assert blended.harmonic_complexity < 0.2
    assert blended.darkness_level < 0.2


def test_interpolation_result_is_clamped():
    """All interpolated values must remain within [0.0, 1.0]."""
    a = StyleSignature(harmonic_complexity=1.0, darkness_level=1.0)
    b = StyleSignature(harmonic_complexity=0.0, darkness_level=0.0)
    blended = a.interpolate(b, weight=0.5)
    assert 0.0 <= blended.harmonic_complexity <= 1.0
    assert 0.0 <= blended.darkness_level <= 1.0


# --- Evaluation Engine Tests ---

def test_originality_exact_cliche():
    """A well-known cliché progression should have near-zero originality."""
    cliche = ["i", "VI", "III", "VII"]
    score = calculate_originality(cliche)
    assert score < 0.2, f"Expected < 0.2 for cliché, got {score}"


def test_originality_novel_progression():
    """An unusual progression should score high originality."""
    novel = ["i", "bII", "v", "bVII", "IV"]
    score = calculate_originality(novel)
    assert score > 0.4, f"Expected > 0.4 for novel, got {score}"


def test_evaluation_result_shape():
    """EvaluationResult should have all four sub-scores and an overall."""
    chords_midi = [[60, 63, 67], [65, 68, 72], [67, 71, 74], [60, 63, 67]]
    chords_roman = ["i", "iv", "v", "i"]
    style = StyleSignature()
    result = evaluate_progression(chords_midi, chords_roman, style)
    assert 0.0 <= result.musical_quality <= 1.0
    assert 0.0 <= result.style_match <= 1.0
    assert 0.0 <= result.originality <= 1.0
    assert 0.0 <= result.emotion <= 1.0
    assert 0.0 <= result.overall_score <= 1.0


# --- Arrangement Engine Tests ---

def test_arrangement_has_correct_sections():
    """Arrangement must always generate at least 3 sections."""
    style = get_artist("Travis Scott").signature
    arr = generate_arrangement("C", "minor", style, total_bars=64)
    assert len(arr.sections) >= 3


def test_arrangement_bar_continuity():
    """Sections must be contiguous (no gaps or overlaps)."""
    style = get_artist("Future").signature
    arr = generate_arrangement("D", "harmonic_minor", style, total_bars=64)
    expected_bar = 0
    for section in arr.sections:
        assert section.start_bar == expected_bar, f"Gap at bar {expected_bar}"
        expected_bar += section.bars


def test_arrangement_hook_has_all_instruments():
    """The Hook section must always have chords, bass, and melody active."""
    style = get_producer("Metro Boomin").signature
    arr = generate_arrangement("F#", "minor", style, total_bars=64)
    hooks = [s for s in arr.sections if "Hook" in s.name]
    assert len(hooks) > 0
    for hook in hooks:
        assert "chords" in hook.active_instruments
        assert "bass" in hook.active_instruments
        assert "melody" in hook.active_instruments


def test_arrangement_intro_has_no_bass():
    """The Intro should have no bass (low energy section)."""
    style = get_producer("Mike Dean").signature
    arr = generate_arrangement("A", "dorian", style, total_bars=64)
    intro = next((s for s in arr.sections if s.name == "Intro"), None)
    assert intro is not None
    assert "bass" not in intro.active_instruments


def test_select_weighted_pitch_prefers_stepwise_motion_for_dense_dark_style():
    """Dense, dark melodic contexts should favor small-step motion over a distant chord tone."""
    style = StyleSignature(
        rhythmic_density=0.85,
        darkness_level=0.9,
        dissonance_tolerance=0.2,
        repetition_tendency=0.7,
    )
    pitch = select_weighted_pitch(
        prev_pitch=60,
        scale_notes=[60, 61, 62, 64, 67],
        current_chord=[60, 64, 67],
        style=style,
        rng=random.Random(7),
        current_tension=0.35,
        recent_pitches=[60, 60],
    )
    assert pitch in {61, 62}


def test_bass_prefers_chord_tones_when_repeating_across_chord_changes():
    """Bass should avoid landing on a non-chord tone simply because the previous bar repeated."""
    style = StyleSignature(root_anchor_prob=0.0, repetition_tendency=0.95, syncopation_level=0.1)
    progression = [[60, 64, 67], [62, 65, 69]]
    from harmonyforge.core import config as cfg

    cfg.seed = 3
    events = generate_808_pattern(progression, style, bpm=120)
    cfg.seed = None

    assert events[1].midi_note % 12 in {2, 5, 9}


def test_melody_prefers_chord_tones_when_nearby_clashes_are_possible():
    """The melody should snap to the nearest chord tone when a semitone clash would occur."""
    style = StyleSignature(rhythmic_density=0.7, darkness_level=0.6, dissonance_tolerance=0.3)
    pitch = select_weighted_pitch(
        prev_pitch=60,
        scale_notes=[60, 61, 62, 64],
        current_chord=[60, 64, 67],
        style=style,
        rng=random.Random(11),
        current_tension=0.2,
        recent_pitches=[60, 60],
    )
    assert pitch in {60, 64}


def test_melody_avoids_semitone_clashes_in_dense_dark_contexts():
    """Dense, dark passages should strongly prefer a chord tone over a semitone clash."""
    style = StyleSignature(rhythmic_density=0.85, darkness_level=0.9, dissonance_tolerance=0.2)
    pitch = select_weighted_pitch(
        prev_pitch=60,
        scale_notes=[60, 61, 64],
        current_chord=[60, 64, 67],
        style=style,
        rng=random.Random(1),
        current_tension=0.7,
        recent_pitches=[60, 60],
    )
    assert pitch == 64


def test_melody_avoids_nearby_clashing_non_chord_tones_in_dark_boundary_contexts():
    """Dark, high-tension melodies should collapse nearby non-chord tones to a chord anchor."""
    style = StyleSignature(rhythmic_density=0.88, darkness_level=0.93, dissonance_tolerance=0.15)
    pitch = select_weighted_pitch(
        prev_pitch=62,
        scale_notes=[60, 61, 62, 64, 67],
        current_chord=[60, 64, 67],
        style=style,
        rng=random.Random(3),
        current_tension=0.82,
        recent_pitches=[62, 62],
    )
    assert pitch in {60, 64}


def test_counter_melody_uses_lower_register_for_dark_styles():
    """Counter melodies should stay out of the lead's bright upper pocket for dark styles."""
    style = StyleSignature(darkness_level=0.9, rhythmic_density=0.8)
    progression = [[60, 64, 67], [60, 64, 67], [60, 64, 67], [60, 64, 67]]
    lead_events = [
        {"midi_note": 72, "start_beat": 0.0, "duration_beats": 1.0, "velocity": 100},
        {"midi_note": 74, "start_beat": 4.0, "duration_beats": 1.0, "velocity": 100},
    ]
    from harmonyforge.generation.melody_generator import MelodyEvent

    lead = [MelodyEvent(**event) for event in lead_events]
    counter = generate_counter_melody(lead, progression, "minor", "C", style, 130)
    assert counter
    assert all(note.midi_note <= 71 for note in counter)


# --- NLP Parser Tests ---

def test_nlp_dark_shifts_darkness():
    """'dark evil' prompt should increase darkness_level."""
    base = StyleSignature(darkness_level=0.3)
    modified = parse_prompt_to_signature("dark evil", base)
    assert modified.darkness_level > base.darkness_level


def test_nlp_happy_decreases_darkness():
    """'happy' prompt should decrease darkness_level."""
    base = StyleSignature(darkness_level=0.6)
    modified = parse_prompt_to_signature("happy", base)
    assert modified.darkness_level < base.darkness_level


def test_nlp_bouncy_increases_syncopation():
    """'bouncy' prompt should increase syncopation_level."""
    base = StyleSignature(syncopation_level=0.2)
    modified = parse_prompt_to_signature("bouncy", base)
    assert modified.syncopation_level > base.syncopation_level


def test_structured_parser_uses_mood_aware_fallback_for_emotional_queries():
    """Emotion-heavy prompts should get a deterministic fallback key/scale instead of always C minor."""
    params = extract_structured_params("emotional melodic beat")
    assert params["key"] == "A"
    assert params["scale"] == "minor"


def test_structured_parser_uses_bright_fallback_for_uplifting_queries():
    """Bright prompts should resolve to a brighter major-key fallback."""
    params = extract_structured_params("happy uplifting beat")
    assert params["key"] == "G"
    assert params["scale"] == "major"


def test_structured_parser_uses_jazzy_fallback_for_complex_queries():
    """Complex prompts should resolve to a modal/jazzy fallback."""
    params = extract_structured_params("jazz complex groove")
    assert params["key"] == "D"
    assert params["scale"] == "dorian"


def test_structured_parser_handles_mixed_mood_words():
    """Mixed mood words should still yield a deterministic fallback candidate."""
    params = extract_structured_params("jazzy bright emotional beat")
    assert params["key"] in {"A", "D", "G"}
    assert params["scale"] in {"minor", "major", "dorian"}


def test_make_command_generates_stems(tmp_path):
    """The natural-language make command should generate MIDI stems."""
    result = runner.invoke(
        app,
        ["make", "dark travis x metro f# 8 bars", "--out-dir", str(tmp_path), "--no-open"],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "dark_travis_x_metro_f_8_bars" / "stem_melody.mid").exists()


def test_root_prompt_generates_stems(tmp_path):
    """A plain prompt should work directly from the root CLI entrypoint."""
    main(["dark travis x metro f# 8 bars", "--out-dir", str(tmp_path), "--no-open"])
    assert (tmp_path / "dark_travis_x_metro_f_8_bars" / "stem_melody.mid").exists()


def test_make_command_with_counter_flag_generates_counter_stem(tmp_path):
    """The make command should honor an explicit counter flag and emit a counter melody stem."""
    result = runner.invoke(
        app,
        ["make", "mike dean type beat", "--out-dir", str(tmp_path), "--no-open", "--counter"],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "mike_dean_type_beat" / "stem_counter_melody.mid").exists()


def test_root_prompt_with_counter_flag_generates_counter_stem(tmp_path):
    """The root prompt-style CLI should honor --counter and emit a counter melody stem."""
    main(["mike dean type beat", "--out-dir", str(tmp_path), "--no-open", "--counter"])
    assert (tmp_path / "mike_dean_type_beat" / "stem_counter_melody.mid").exists()


def test_humanize_instrument_is_deterministic_and_grid_aligned():
    """Humanization should be stable and keep notes aligned to a shared 16th-note grid."""
    inst = pretty_midi.Instrument(program=0, name="test")
    inst.notes.append(pretty_midi.Note(velocity=90, pitch=60, start=0.18, end=0.42))
    inst.notes.append(pretty_midi.Note(velocity=80, pitch=64, start=0.43, end=0.70))

    inst_copy = copy.deepcopy(inst)
    humanize_instrument(inst, style_name="trap_bounce", bpm=120.0, swing_strength=0.2)
    humanize_instrument(inst_copy, style_name="trap_bounce", bpm=120.0, swing_strength=0.2)

    assert inst.notes[0].start == inst_copy.notes[0].start
    assert inst.notes[0].end == inst_copy.notes[0].end
    assert abs(inst.notes[0].start % (60.0 / 120.0 / 4.0)) < 1e-9


def test_export_loop_leaves_notes_unhumanized_by_default(tmp_path):
    """Export should stay grid-straight unless humanization is explicitly enabled."""
    from types import SimpleNamespace

    from harmonyforge.generation.bass_generator import BassEvent
    from harmonyforge.generation.melody_generator import MelodyEvent
    from harmonyforge.midi.exporter import export_loop

    progression = SimpleNamespace(chord_events=[], chords_midi=[[60, 64, 67]], bpm=120)
    melody = [MelodyEvent(midi_note=72, start_beat=0.0, duration_beats=1.0, velocity=100)]
    bass = [BassEvent(midi_note=48, start_beat=0.0, duration_beats=1.0, velocity=100, pitch_bend=0)]

    export_loop(progression, melody, bass, tmp_path, bpm=120)

    midi = pretty_midi.PrettyMIDI(str(tmp_path / "stem_melody.mid"))
    note = midi.instruments[0].notes[0]

    assert note.start == 0.0
    assert note.end == 0.5


def test_version_flag_prints_release_info(capsys):
    """The CLI should expose a version flag for quick confirmation."""
    main(["--version"])
    captured = capsys.readouterr()
    assert "harmonyforge" in captured.out.lower()
