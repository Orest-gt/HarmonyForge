"""
Inverted Harmonic Gravity Field - Crash Tests

Testing edge cases and extreme conditions:
1. Inversion Crash Test: Chord change at boundary with max tension
2. Octave Jump Elasticity: Magnetic collapse behavior
3. Musical Instinct: Boundary resolution quality
"""

from harmonyforge.generation.melody_generator import (
    compute_harmonic_pull,
    detect_resolution_window,
    magnetic_collapse,
    MelodyEvent
)
import random

def test_inversion_crash():
    """Test what happens when chord changes at boundary with max tension."""
    print("=" * 60)
    print("TEST 1: Inversion Crash Test")
    print("=" * 60)
    
    # Setup: High tension pitch approaching boundary
    current_pitch = 72  # C5
    old_chord = [60, 64, 67]  # C major triad
    new_chord = [65, 69, 72]  # F major triad (different chord tones)
    scale_notes = list(range(60, 85))  # C4 to C6
    
    # Maximum tension scenario
    max_tension = 1.0
    
    # At exact boundary (beat 4.0 in 8-bar phrase)
    boundary_beat = 4.0
    magnetic_strength = detect_resolution_window(boundary_beat, 8.0)
    
    print(f"Current pitch: {current_pitch} (C5)")
    print(f"Old chord: {old_chord} (C major)")
    print(f"New chord: {new_chord} (F major)")
    print(f"Max tension: {max_tension}")
    print(f"Boundary beat: {boundary_beat}")
    print(f"Magnetic strength: {magnetic_strength:.3f}")
    
    # Test gravitational pull from OLD chord
    pull_old = compute_harmonic_pull(current_pitch, old_chord, max_tension)
    print(f"Gravitational pull from OLD chord: {pull_old:.3f}")
    
    # Test gravitational pull from NEW chord
    pull_new = compute_harmonic_pull(current_pitch, new_chord, max_tension)
    print(f"Gravitational pull from NEW chord: {pull_new:.3f}")
    
    # Test magnetic collapse with NEW chord
    rng = random.Random(42)
    collapsed_pitch = magnetic_collapse(current_pitch, new_chord, scale_notes, magnetic_strength, rng)
    
    print(f"Original pitch: {current_pitch}")
    print(f"Collapsed pitch: {collapsed_pitch}")
    print(f"Pitch jumped: {abs(collapsed_pitch - current_pitch)} semitones")
    
    # Analysis
    if collapsed_pitch % 12 in [c % 12 for c in new_chord]:
        print("[PASS] Magnetic collapse respects NEW chord")
    else:
        print("[FAIL] Magnetic collapse IGNORED new chord (INVERSION CRASH)")
    
    print()

def test_octave_jump_elasticity():
    """Test whether magnetic collapse prefers pitch proximity or tonal center."""
    print("=" * 60)
    print("TEST 2: Octave Jump Elasticity")
    print("=" * 60)
    
    # Setup: Mid-range pitch, chord with options at different distances
    current_pitch = 72  # C5
    chord = [48, 60, 72, 84]  # C major at multiple octaves
    scale_notes = list(range(48, 85))  # C3 to C6
    
    # High magnetic strength (boundary condition)
    magnetic_strength = 0.9
    
    print(f"Current pitch: {current_pitch} (C5)")
    print(f"Chord tones: {chord} (C major at C3, C4, C5, C6)")
    print(f"Magnetic strength: {magnetic_strength}")
    
    # Distance analysis
    for chord_tone in chord:
        distance = abs(chord_tone - current_pitch)
        print(f"Distance to {chord_tone}: {distance} semitones")
    
    # Test magnetic collapse
    rng = random.Random(42)
    collapsed_pitch = magnetic_collapse(current_pitch, chord, scale_notes, magnetic_strength, rng)
    
    print(f"Collapsed to: {collapsed_pitch}")
    print(f"Distance from original: {abs(collapsed_pitch - current_pitch)} semitones")
    
    # Analysis
    nearest_chord_tone = min(chord, key=lambda c: abs(c - current_pitch))
    if collapsed_pitch == nearest_chord_tone:
        print("[PASS] Magnetic collapse prefers PITCH PROXIMITY")
    elif collapsed_pitch == current_pitch:
        print("[WARN] Magnetic collapse stayed at original pitch")
    else:
        print("[FAIL] Magnetic collapse chose non-nearest chord tone")
    
    print()

def test_musical_instinct_boundaries():
    """Test if melody boundaries sound inevitable (not just correct)."""
    print("=" * 60)
    print("TEST 3: Musical Instinct at Boundaries")
    print("=" * 60)
    
    # Simulate boundary approach with varying tension
    scale_notes = list(range(60, 85))
    chord = [60, 64, 67]  # C major
    rng = random.Random(42)
    
    test_cases = [
        (3.8, 0.8, "Near boundary - strong magnetic pull"),
        (3.9, 0.9, "Very near boundary - very strong magnetic pull"),
        (4.0, 1.0, "AT boundary - maximum magnetic pull"),
        (4.1, 0.9, "Just past boundary - very strong magnetic pull"),
    ]
    
    for beat, expected_strength, description in test_cases:
        magnetic_strength = detect_resolution_window(beat, 8.0)
        print(f"{description}")
        print(f"  Beat: {beat}, Magnetic strength: {magnetic_strength:.3f} (expected: {expected_strength})")
        
        # Test collapse with tension
        test_pitch = 74  # D5 (non-chord tone)
        tension = 0.8  # High tension
        collapsed = magnetic_collapse(test_pitch, chord, scale_notes, magnetic_strength, rng)
        
        print(f"  Test pitch: {test_pitch} (D5 - non-chord tone)")
        print(f"  Tension: {tension}")
        print(f"  Collapsed to: {collapsed}")
        
        if collapsed % 12 in [c % 12 for c in chord]:
            print(f"  ✅ Collapsed to chord tone (inevitable resolution)")
        else:
            print(f"  ❌ Failed to collapse to chord tone (weak instinct)")
        
        print()

def test_tension_field_dynamics():
    """Test tension accumulation and release patterns."""
    print("=" * 60)
    print("TEST 4: Tension Field Dynamics")
    print("=" * 60)
    
    chord = [60, 64, 67]  # C major
    non_chord_tones = [62, 65, 69]  # D, F, A (scale degrees but not chord tones)
    
    print("Chord tones:", chord)
    print("Non-chord tones:", non_chord_tones)
    print()
    
    # Test tension accumulation on non-chord tones
    print("Tension Accumulation:")
    for pitch in non_chord_tones:
        nearest_chord = min(chord, key=lambda c: abs(pitch - c))
        distance = abs(pitch - nearest_chord)
        tension_increment = distance * 1.0  # duration = 1 beat
        print(f"  Pitch {pitch}: distance {distance} semitones → tension +{tension_increment}")
    
    print()
    
    # Test tension release on chord tones
    print("Tension Release:")
    initial_tension = 1.0
    for pitch in chord:
        released_tension = initial_tension * 0.7  # decay factor
        print(f"  Pitch {pitch}: tension {initial_tension} → {released_tension} (decay factor 0.7)")
    
    print()

if __name__ == "__main__":
    test_inversion_crash()
    test_octave_jump_elasticity()
    test_musical_instinct_boundaries()
    test_tension_field_dynamics()
    
    print("=" * 60)
    print("CRASH TEST SUMMARY")
    print("=" * 60)
    print("Analyze the results above for:")
    print("1. Inversion Crash: Does magnetic collapse respect NEW chords at boundaries?")
    print("2. Octave Elasticity: Does it prefer proximity or tonal center?")
    print("3. Musical Instinct: Do boundaries sound inevitable?")
    print("4. Tension Dynamics: Are accumulation/release patterns musical?")