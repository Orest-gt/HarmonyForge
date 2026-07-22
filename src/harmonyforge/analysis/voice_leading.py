"""
Voice leading analysis and scoring engine.
Evaluates the smoothness of chord transitions.
"""

from typing import List

def calculate_voice_leading_score(chord_a: List[int], chord_b: List[int]) -> float:
    """
    Calculates a voice leading score between 0.0 and 1.0.
    1.0 means minimal movement (very smooth).
    0.0 means large, awkward leaps.
    """
    if not chord_a or not chord_b:
        return 0.0
        
    # Ensure lists are sorted from bottom to top
    a = sorted(chord_a)
    b = sorted(chord_b)
    
    # Calculate bass movement (lowest note)
    bass_diff = abs(a[0] - b[0])
    
    # A perfect 5th or 4th in the bass is actually good for root movement,
    # but for pure smoothness we penalize large intervals.
    # We will score bass movement differently (e.g., jumps > 12 are bad).
    bass_penalty = max(0, (bass_diff - 12)) * 0.1
    
    # Calculate upper voice movement (approximate by matching lengths)
    # If chord sizes differ, we just match up to the min length
    min_len = min(len(a), len(b))
    total_movement = 0
    for i in range(1, min_len):
        total_movement += abs(a[i] - b[i])
        
    # Average movement per voice (excluding bass)
    avg_movement = total_movement / max(1, (min_len - 1))
    
    # Map movement to a 0-1 scale. 
    # An average movement of 0 is perfect (1.0). 
    # An average movement of 7+ semitones is poor (0.0).
    movement_score = max(0.0, 1.0 - (avg_movement / 7.0))
    
    # Final score combines upper voice smoothness with bass penalty
    final_score = movement_score - bass_penalty
    return max(0.0, min(1.0, final_score))

def analyze_progression_voice_leading(progression_midi: List[List[int]]) -> float:
    """
    Returns the average voice leading score for an entire progression.
    """
    if len(progression_midi) < 2:
        return 1.0
        
    scores = []
    for i in range(len(progression_midi) - 1):
        scores.append(calculate_voice_leading_score(progression_midi[i], progression_midi[i+1]))
        
    return sum(scores) / len(scores)
