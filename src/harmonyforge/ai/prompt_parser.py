"""
Prompt parser — Musical Vocabulary Ontology only.

The PyTorch neural net (LightweightStylePredictor) is intentionally excluded
from the v1.0 core path. Install the [ai] optional extra to enable it.
"""

from typing import Dict
from harmonyforge.styles.genome import StyleSignature

# Musical Vocabulary Ontology: word → genome parameter shifts
ONTOLOGY: Dict[str, Dict[str, float]] = {
    # Aesthetic / Emotion
    "evil":      {"darkness_level": 0.2,  "dissonance_tolerance": 0.15, "tension_preference": 0.2},
    "luxury":    {"harmonic_complexity": 0.15, "repetition_tendency": -0.1},
    "ambient":   {"rhythmic_density": -0.2, "harmonic_complexity": 0.1, "repetition_tendency": 0.15},
    "spacey":    {"rhythmic_density": -0.1, "modal_interchange_prob": 0.1},
    "dark":      {"darkness_level": 0.15, "tension_preference": 0.1},
    "happy":     {"darkness_level": -0.3, "tension_preference": -0.2},
    "emotional": {"harmonic_complexity": 0.1, "tension_preference": 0.1, "modal_interchange_prob": 0.1},
    "cinematic": {"harmonic_complexity": 0.2, "modal_interchange_prob": 0.15, "tension_preference": 0.1},
    "aggressive":{"dissonance_tolerance": 0.2, "rhythmic_density": 0.2, "tension_preference": 0.15},
    "melancholy":{"darkness_level": 0.1,  "tension_preference": 0.05, "harmonic_complexity": 0.1},
    # Rhythm / Groove
    "bouncy":    {"syncopation_level": 0.2, "rhythmic_density": 0.1},
    "fast":      {"rhythmic_density": 0.2},
    "slow":      {"rhythmic_density": -0.2},
    "sparse":    {"rhythmic_density": -0.15, "repetition_tendency": 0.1},
    "dense":     {"rhythmic_density": 0.2,  "syncopation_level": 0.1},
    # Complexity
    "complex":   {"harmonic_complexity": 0.2, "secondary_dominant_prob": 0.15},
    "simple":    {"harmonic_complexity": -0.2, "repetition_tendency": 0.2},
    "jazz":      {"harmonic_complexity": 0.25, "secondary_dominant_prob": 0.2, "modal_interchange_prob": 0.15},
}


def parse_prompt_to_signature(prompt: str, base_signature: StyleSignature) -> StyleSignature:
    """
    Converts a natural-language prompt into genome parameter shifts
    using the Musical Vocabulary Ontology. No external dependencies required.
    """
    words = prompt.lower().replace(",", "").replace(".", "").split()

    shifts: Dict[str, float] = {
        "harmonic_complexity": 0.0,
        "dissonance_tolerance": 0.0,
        "modal_interchange_prob": 0.0,
        "secondary_dominant_prob": 0.0,
        "rhythmic_density": 0.0,
        "syncopation_level": 0.0,
        "repetition_tendency": 0.0,
        "darkness_level": 0.0,
        "tension_preference": 0.0,
    }

    for word in words:
        if word in ONTOLOGY:
            for param, delta in ONTOLOGY[word].items():
                shifts[param] += delta

    def clamp(base: float, shift: float) -> float:
        return max(0.0, min(1.0, base + shift))

    return StyleSignature(
        harmonic_complexity=clamp(base_signature.harmonic_complexity,    shifts["harmonic_complexity"]),
        dissonance_tolerance=clamp(base_signature.dissonance_tolerance,   shifts["dissonance_tolerance"]),
        modal_interchange_prob=clamp(base_signature.modal_interchange_prob, shifts["modal_interchange_prob"]),
        secondary_dominant_prob=clamp(base_signature.secondary_dominant_prob, shifts["secondary_dominant_prob"]),
        rhythmic_density=clamp(base_signature.rhythmic_density,           shifts["rhythmic_density"]),
        syncopation_level=clamp(base_signature.syncopation_level,         shifts["syncopation_level"]),
        repetition_tendency=clamp(base_signature.repetition_tendency,     shifts["repetition_tendency"]),
        melodic_range=base_signature.melodic_range,
        darkness_level=clamp(base_signature.darkness_level,               shifts["darkness_level"]),
        tension_preference=clamp(base_signature.tension_preference,       shifts["tension_preference"]),
        preferred_scales=base_signature.preferred_scales,
        preferred_chord_types=base_signature.preferred_chord_types,
        preferred_bpm_range=base_signature.preferred_bpm_range,
    )
