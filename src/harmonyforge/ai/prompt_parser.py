"""
Prompt parser utilizing the lightweight AI models and a musical vocabulary ontology.
"""

from typing import Dict
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.ai.models import mock_predict_style

# Musical Vocabulary Ontology
ONTOLOGY: Dict[str, Dict[str, float]] = {
    # Aesthetic / Emotion
    "evil": {"darkness_level": 0.2, "dissonance_tolerance": 0.15, "tension_preference": 0.2},
    "luxury": {"harmonic_complexity": 0.15, "repetition_tendency": -0.1},
    "ambient": {"rhythmic_density": -0.2, "harmonic_complexity": 0.1, "repetition_tendency": 0.15},
    "spacey": {"rhythmic_density": -0.1, "modal_interchange_prob": 0.1},
    "dark": {"darkness_level": 0.15, "tension_preference": 0.1},
    "happy": {"darkness_level": -0.3, "tension_preference": -0.2},
    "emotional": {"harmonic_complexity": 0.1, "tension_preference": 0.1, "modal_interchange_prob": 0.1},
    
    # Rhythm / Groove
    "bouncy": {"syncopation_level": 0.2, "rhythmic_density": 0.1},
    "fast": {"rhythmic_density": 0.2},
    "slow": {"rhythmic_density": -0.2},
    
    # Complexity
    "complex": {"harmonic_complexity": 0.2, "secondary_dominant_prob": 0.15},
    "simple": {"harmonic_complexity": -0.2, "repetition_tendency": 0.2},
}

def parse_prompt_to_signature(prompt: str, base_signature: StyleSignature) -> StyleSignature:
    """
    Uses the Musical Vocabulary Ontology and PyTorch StylePredictor 
    to convert natural language into genome parameter shifts.
    """
    # 1. Base prediction from neural net (LightweightStylePredictor)
    nn_predictions = mock_predict_style(prompt)
    nn_complexity_shift = (nn_predictions[0] - 0.5) * 0.1 if nn_predictions else 0.0
    
    # 2. Ontology-based precise shifts
    words = prompt.lower().replace(",", "").replace(".", "").split()
    
    shifts: Dict[str, float] = {
        "harmonic_complexity": nn_complexity_shift,
        "dissonance_tolerance": 0.0,
        "modal_interchange_prob": 0.0,
        "secondary_dominant_prob": 0.0,
        "rhythmic_density": 0.0,
        "syncopation_level": 0.0,
        "repetition_tendency": 0.0,
        "darkness_level": 0.0,
        "tension_preference": 0.0
    }
    
    for word in words:
        if word in ONTOLOGY:
            for key, shift_val in ONTOLOGY[word].items():
                shifts[key] += shift_val
                
    # 3. Apply shifts to the base signature
    def apply_shift(base_val: float, shift: float) -> float:
        return max(0.0, min(1.0, base_val + shift))
        
    return StyleSignature(
        harmonic_complexity=apply_shift(base_signature.harmonic_complexity, shifts["harmonic_complexity"]),
        dissonance_tolerance=apply_shift(base_signature.dissonance_tolerance, shifts["dissonance_tolerance"]),
        modal_interchange_prob=apply_shift(base_signature.modal_interchange_prob, shifts["modal_interchange_prob"]),
        secondary_dominant_prob=apply_shift(base_signature.secondary_dominant_prob, shifts["secondary_dominant_prob"]),
        rhythmic_density=apply_shift(base_signature.rhythmic_density, shifts["rhythmic_density"]),
        syncopation_level=apply_shift(base_signature.syncopation_level, shifts["syncopation_level"]),
        repetition_tendency=apply_shift(base_signature.repetition_tendency, shifts["repetition_tendency"]),
        melodic_range=base_signature.melodic_range,
        darkness_level=apply_shift(base_signature.darkness_level, shifts["darkness_level"]),
        tension_preference=apply_shift(base_signature.tension_preference, shifts["tension_preference"]),
        preferred_scales=base_signature.preferred_scales,
        preferred_chord_types=base_signature.preferred_chord_types,
        preferred_bpm_range=base_signature.preferred_bpm_range
    )
