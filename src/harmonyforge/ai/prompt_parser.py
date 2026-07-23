"""
Prompt parser — two modes:

1. `parse_prompt_to_signature(prompt, base_sig)`
   Musical Vocabulary Ontology: word → genome parameter shifts.
   Used by `generate` command for --prompt flag.

2. `extract_structured_params(query)`
   Full natural-language extraction for the `make` command.
   Detects: producer, artist, key, scale, BPM, bars, swing, flags, and residual mood words.
"""

import re
from typing import Dict, Any, Match
from harmonyforge.styles.genome import StyleSignature


# ---------------------------------------------------------------------------
# Musical Vocabulary Ontology — word → genome parameter shifts
# ---------------------------------------------------------------------------
ONTOLOGY: Dict[str, Dict[str, float]] = {
    # Aesthetic / Emotion
    "evil":       {"darkness_level": 0.2,  "dissonance_tolerance": 0.15, "tension_preference": 0.2},
    "luxury":     {"harmonic_complexity": 0.15, "repetition_tendency": -0.1},
    "ambient":    {"rhythmic_density": -0.2, "harmonic_complexity": 0.1, "repetition_tendency": 0.15},
    "spacey":     {"rhythmic_density": -0.1, "modal_interchange_prob": 0.1},
    "dark":       {"darkness_level": 0.15, "tension_preference": 0.1},
    "happy":      {"darkness_level": -0.3, "tension_preference": -0.2},
    "emotional":  {"harmonic_complexity": 0.1, "tension_preference": 0.1, "modal_interchange_prob": 0.1},
    "cinematic":  {"harmonic_complexity": 0.2, "modal_interchange_prob": 0.15, "tension_preference": 0.1},
    "aggressive": {"dissonance_tolerance": 0.2, "rhythmic_density": 0.2, "tension_preference": 0.15},
    "melancholy": {"darkness_level": 0.1,  "tension_preference": 0.05, "harmonic_complexity": 0.1},
    "trap":       {"darkness_level": 0.1,  "syncopation_level": 0.1},
    "drill":      {"darkness_level": 0.15, "rhythmic_density": 0.1, "tension_preference": 0.1},
    "rage":       {"dissonance_tolerance": 0.2, "rhythmic_density": 0.2},
    "melodic":    {"harmonic_complexity": 0.15, "modal_interchange_prob": 0.1},
    "dreamy":     {"rhythmic_density": -0.15, "harmonic_complexity": 0.1, "modal_interchange_prob": 0.15},
    # Rhythm / Groove
    "bouncy":     {"syncopation_level": 0.2, "rhythmic_density": 0.1},
    "fast":       {"rhythmic_density": 0.2},
    "slow":       {"rhythmic_density": -0.2},
    "sparse":     {"rhythmic_density": -0.15, "repetition_tendency": 0.1},
    "dense":      {"rhythmic_density": 0.2,  "syncopation_level": 0.1},
    # Complexity
    "complex":    {"harmonic_complexity": 0.2, "secondary_dominant_prob": 0.15},
    "simple":     {"harmonic_complexity": -0.2, "repetition_tendency": 0.2},
    "jazz":       {"harmonic_complexity": 0.25, "secondary_dominant_prob": 0.2, "modal_interchange_prob": 0.15},
}


def parse_prompt_to_signature(prompt: str, base_signature: StyleSignature) -> StyleSignature:
    """
    Converts a natural-language prompt into genome parameter shifts
    using the Musical Vocabulary Ontology. No external dependencies required.
    """
    words = prompt.lower().replace(",", "").replace(".", "").split()

    shifts: Dict[str, float] = {k: 0.0 for k in [
        "harmonic_complexity", "dissonance_tolerance", "modal_interchange_prob",
        "secondary_dominant_prob", "rhythmic_density", "syncopation_level",
        "repetition_tendency", "darkness_level", "tension_preference",
    ]}

    for word in words:
        if word in ONTOLOGY:
            for param, delta in ONTOLOGY[word].items():
                shifts[param] += delta

    def clamp(base: float, shift: float) -> float:
        return max(0.0, min(1.0, base + shift))

    return StyleSignature(
        harmonic_complexity=clamp(base_signature.harmonic_complexity,      shifts["harmonic_complexity"]),
        dissonance_tolerance=clamp(base_signature.dissonance_tolerance,    shifts["dissonance_tolerance"]),
        modal_interchange_prob=clamp(base_signature.modal_interchange_prob, shifts["modal_interchange_prob"]),
        secondary_dominant_prob=clamp(base_signature.secondary_dominant_prob, shifts["secondary_dominant_prob"]),
        rhythmic_density=clamp(base_signature.rhythmic_density,            shifts["rhythmic_density"]),
        syncopation_level=clamp(base_signature.syncopation_level,          shifts["syncopation_level"]),
        repetition_tendency=clamp(base_signature.repetition_tendency,      shifts["repetition_tendency"]),
        melodic_range=base_signature.melodic_range,
        darkness_level=clamp(base_signature.darkness_level,                shifts["darkness_level"]),
        tension_preference=clamp(base_signature.tension_preference,        shifts["tension_preference"]),
        preferred_scales=base_signature.preferred_scales,
        preferred_chord_types=base_signature.preferred_chord_types,
        preferred_bpm_range=base_signature.preferred_bpm_range,
    )


# ---------------------------------------------------------------------------
# Natural-language structured extraction for `harmonyforge make`
# ---------------------------------------------------------------------------

# Scale vibes: keyword → internal scale name
_SCALE_VIBES = {
    "phrygian": "phrygian",
    "spanish":  "phrygian",
    "flamenco": "phrygian",
    "harmonic": "harmonic_minor",
    "dramatic": "harmonic_minor",
    "haunting": "harmonic_minor",
    "dorian":   "dorian",
    "soulful":  "dorian",
    "modal":    "dorian",
    "major":    "major",
    "happy":    "major",
    "bright":   "major",
    "lydian":   "lydian",
    "minor":    "minor",
    "sad":      "minor",
    # NOTE: "evil" is intentionally absent — it's a mood/genome word, not a scale selector.
    # "evil bb minor" → scale=minor, genome shifts toward phrygian darkness via ONTOLOGY.
}

# Swing vibes: keyword → swing template name
_SWING_VIBES = {
    "trap":      "trap_bounce",
    "bounce":    "trap_bounce",
    "bouncy":    "trap_bounce",
    "dilla":     "dilla_swing",
    "lazy":      "dilla_swing",
    "neo-soul":  "dilla_swing",
    "neosoul":   "dilla_swing",
    "drill":     "drill_push",
    "push":      "drill_push",
    "afro":      "afro_triplet",
    "afrobeat":  "afro_triplet",
    "straight":  "straight",
}

# Default swing per darkness level (used when no swing keyword found)
def _default_swing(darkness: float, density: float) -> str:
    if density > 0.75:
        return "drill_push"
    if darkness > 0.75:
        return "trap_bounce"
    if darkness < 0.5:
        return "dilla_swing"
    return "trap_bounce"


def _build_alias_map(db: dict[str, Any]) -> dict[str, str]:
    """Build { lowercased_name_or_alias: db_key } from any profile DB."""
    alias_map = {}
    for db_key, profile in db.items():
        alias_map[profile.name.lower()] = db_key
        for alias in getattr(profile, "aliases", []) or []:
            alias_map[alias.lower()] = db_key
    return alias_map


def extract_structured_params(query: str) -> dict[str, Any]:
    """
    Parses a free-form natural language string into structured generation params.

    Detects (in priority order):
      - Producer names + aliases  (e.g. "metro boomin", "Metro", "Tay Keith")
      - Artist names + aliases    (e.g. "Travis", "La Flame")
      - Musical key               (e.g. "F#", "Bb", "D")
      - Scale / vibe              (e.g. "minor", "harmonic", "phrygian", "evil")
      - BPM                       (e.g. "145 bpm", "at 163")
      - Bars                      (e.g. "8 bars", "16 bar")
      - Swing template            (e.g. "dilla", "trap", "drill")
      - Stem flags                (counter, vocal)
      - Residual mood words       → fed into ONTOLOGY genome shifts

    Returns a dict with keys:
        producers, artists, key, scale, bpm, bars, swing, counter, vocal, mood_words
    """
    # Lazy import to avoid circular dependency at module level
    from harmonyforge.styles.artists import ARTISTS_DB
    from harmonyforge.styles.producers import PRODUCERS_DB

    raw = query.strip()
    text = raw.lower()
    text_norm = re.sub(r"[,.\-!?;:]", " ", text)

    result: dict[str, Any] = {
        "producers":  [],
        "artists":    [],
        "key":        "C",
        "scale":      "minor",
        "bpm":        None,
        "bars":       8,
        "swing":      None,    # resolved later if not found
        "counter":    False,
        "vocal":      False,
        "mood_words": [],
    }
    
    # Type assertions for mypy
    producers_list: list[str] = result["producers"]  # type: ignore
    artists_list: list[str] = result["artists"]      # type: ignore
    mood_words_list: list[str] = result["mood_words"]  # type: ignore

    consumed_spans: list[tuple[int, int]] = []   # list of (start, end) char spans consumed

    def mark(m: Match[str]) -> None:
        consumed_spans.append((m.start(), m.end()))

    def is_consumed(start: int, end: int) -> bool:
        return any(s <= start < e or s < end <= e for s, e in consumed_spans)

    # ---- 1. Producer detection (multi-word first, then single) ----
    producer_aliases = _build_alias_map(PRODUCERS_DB)
    for alias in sorted(producer_aliases, key=len, reverse=True):
        pattern = r"\b" + re.escape(alias) + r"\b"
        for m in re.finditer(pattern, text_norm):
            if not is_consumed(m.start(), m.end()):
                db_key = producer_aliases[alias]
                if db_key not in producers_list:
                    producers_list.append(db_key)
                mark(m)

    # ---- 2. Artist detection ----
    artist_aliases = _build_alias_map(ARTISTS_DB)
    for alias in sorted(artist_aliases, key=len, reverse=True):
        pattern = r"\b" + re.escape(alias) + r"\b"
        for m in re.finditer(pattern, text_norm):
            if not is_consumed(m.start(), m.end()):
                db_key = artist_aliases[alias]
                if db_key not in artists_list:
                    artists_list.append(db_key)
                mark(m)

    # ---- 3. BPM detection: "145 bpm" or "at 145" ----
    for pattern in [r"\b(\d{2,3})\s*bpm\b", r"\bat\s+(\d{2,3})\b"]:
        m_match = re.search(pattern, text_norm)
        if m_match:
            result["bpm"] = int(m_match.group(1))
            mark(m_match)
            break

    # ---- 4. Bars detection: "8 bars" ----
    bars_match = re.search(r"\b(\d+)\s*bars?\b", text_norm)
    if bars_match:
        result["bars"] = max(2, min(64, int(bars_match.group(1))))
        mark(bars_match)

    # ---- 5. Key detection ----
    # Note: # and b are NOT \w chars, so \b after them fails.
    # Use lookahead (?=\s|$) instead of \b after the note name.
    _KEY_NAMES_PAT = r"(?:minor|major|phrygian|harmonic|dorian|lydian|diminished)"
    _NOTE_PAT      = r"([a-g][#b]?)"
    # Pattern A: note + scale word (e.g. "f# minor", "c dorian")
    # IMPORTANT: only mark the note span, NOT the scale keyword — scale detection handles that separately.
    key_match = re.search(_NOTE_PAT + r"(?=\s+" + _KEY_NAMES_PAT + r")", text_norm)
    if key_match:
        note = key_match.group(1)
        result["key"] = note[0].upper() + note[1:]
        mark(key_match)   # Only the note token is marked
    else:
        # Pattern B: "key f#" or "in f#"
        key_match = re.search(r"\bkey\s+(?:of\s+)?" + _NOTE_PAT + r"(?=\s|$)", text_norm)
        if key_match:
            note = key_match.group(1)
            result["key"] = note[0].upper() + note[1:]
            mark(key_match)
        else:
            # Pattern C: isolated note token (e.g. "travis x metro f# 8 bars")
            for m2 in re.finditer(r"(?<=\s)(" + _NOTE_PAT[1:-1] + r")(?=\s|$)", text_norm):
                candidate = m2.group(1)
                if not is_consumed(m2.start(), m2.end()):
                    result["key"] = candidate[0].upper() + candidate[1:]
                    mark(m2)
                    break

    # ---- 6. Scale vibe ----
    # Priority order: most-specific first. Stop at first match.
    # 'evil' is intentionally NOT here — it's a mood word, not a scale selector.
    # When user says 'evil bb minor', the scale is 'minor'; evil just shifts the genome.
    _SCALE_PRIORITY = [
        "phrygian", "flamenco", "spanish",
        "harmonic", "dramatic", "haunting",
        "dorian", "soulful", "modal",
        "lydian",
        "major", "happy", "bright",
        "minor", "sad",
    ]
    for kw in _SCALE_PRIORITY:
        scale_match = re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", text_norm)
        if scale_match and not is_consumed(scale_match.start(), scale_match.end()):
            result["scale"] = _SCALE_VIBES[kw]
            mark(scale_match)
            break   # STOP — first specific match wins

    # ---- 7. Swing template ----
    for kw in sorted(_SWING_VIBES, key=len, reverse=True):
        swing_match = re.search(r"\b" + re.escape(kw) + r"\b", text_norm)
        if swing_match and not is_consumed(swing_match.start(), swing_match.end()):
            result["swing"] = _SWING_VIBES[kw]
            mark(swing_match)
            break

    # ---- 8. Stem flags ----
    if re.search(r"\b(?:counter|fills?|response|countermelody)\b", text_norm):
        result["counter"] = True
    if re.search(r"\b(?:vocal|vocals?|topline|hook|singable)\b", text_norm):
        result["vocal"] = True

    # ---- 9. Residual mood words (for genome ONTOLOGY shifts) ----
    _STOP = {"a", "an", "the", "in", "at", "of", "for", "me", "make", "like",
             "and", "with", "give", "get", "x", "some", "something", "want",
             "bars", "bar", "bpm", "key"}
    words = text_norm.split()
    for i, w in enumerate(words):
        word_start = sum(len(ww) + 1 for ww in words[:i])
        word_end   = word_start + len(w)
        if (not is_consumed(word_start, word_end)
                and w.isalpha()
                and len(w) > 2
                and w not in _STOP
                and w in ONTOLOGY):
            mood_words_list.append(w)

    return result
