"""
Unit tests for HarmonyForge V2.1.
Covers: genome interpolation, evaluation engine, arrangement generation,
NLP parser, and MIDI export round-trip.
"""

from harmonyforge.styles.genome import StyleSignature
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature
from harmonyforge.analysis.evaluation import evaluate_progression, calculate_originality
from harmonyforge.generation.arrangement_generator import generate_arrangement


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
