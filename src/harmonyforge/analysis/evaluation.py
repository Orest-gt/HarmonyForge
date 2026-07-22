"""
Evaluation Engine V2.
Features a database of generic progressions for true originality scoring.
Calculates Musical Quality, Style Match, Originality, and Emotional Impact.
"""

from typing import List
from pydantic import BaseModel

from harmonyforge.styles.genome import StyleSignature
from harmonyforge.analysis.voice_leading import analyze_progression_voice_leading

# Common / Cliché trap and pop chord progressions (Roman Numerals)
GENERIC_PROGRESSIONS = [
    ["i", "VI", "III", "VII"],
    ["i", "iv", "v", "i"],
    ["i", "VII", "VI", "V"],
    ["vi", "IV", "I", "V"],
    ["I", "V", "vi", "IV"],
    ["i", "VI", "iv", "V"],
    ["i", "v", "iv", "v"],
]

class EvaluationResult(BaseModel):
    musical_quality: float
    style_match: float
    originality: float
    emotion: float
    overall_score: float

def calculate_originality(progression_roman: List[str]) -> float:
    """
    Calculates originality by finding the maximum similarity to known generic progressions.
    1.0 means highly original (unseen), 0.0 means exact match with a cliché.
    """
    if not progression_roman:
        return 1.0
        
    max_similarity = 0.0
    # Normalize our progression to check subsets
    prog_len = len(progression_roman)
    
    for generic in GENERIC_PROGRESSIONS:
        gen_len = len(generic)
        # Check rolling windows
        for i in range(max(1, prog_len - gen_len + 1)):
            window = progression_roman[i:i+gen_len]
            matches = sum(1 for a, b in zip(window, generic) if a.lower() == b.lower())
            sim = matches / gen_len
            if sim > max_similarity:
                max_similarity = sim
                
    return max(0.0, 1.0 - max_similarity)

def evaluate_style_match(prog_midi: List[List[int]], target_style: StyleSignature) -> float:
    # Heuristic based on harmonic complexity (7th/9th chord density)
    complexity_score = sum(1 for chord in prog_midi if len(chord) > 3) / max(1, len(prog_midi))
    diff = abs(target_style.harmonic_complexity - complexity_score)
    return max(0.0, 1.0 - diff)
    
def evaluate_emotion(prog_midi: List[List[int]], target_style: StyleSignature) -> float:
    # Example heuristic: darker styles prefer more minor/dim intervals
    # For now, it returns a score bounded by tension_preference
    return max(0.0, min(1.0, target_style.tension_preference + 0.1))

def evaluate_progression(prog_midi: List[List[int]], prog_roman: List[str], target_style: StyleSignature) -> EvaluationResult:
    quality = analyze_progression_voice_leading(prog_midi)
    style = evaluate_style_match(prog_midi, target_style)
    originality = calculate_originality(prog_roman)
    emotion = evaluate_emotion(prog_midi, target_style)
    
    # Weighted evaluation
    overall = (quality * 0.3) + (style * 0.3) + (originality * 0.2) + (emotion * 0.2)
    
    return EvaluationResult(
        musical_quality=quality,
        style_match=style,
        originality=originality,
        emotion=emotion,
        overall_score=overall
    )
