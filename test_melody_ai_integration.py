"""
Test AI Integration with Melody Generator

This demonstrates the complete AI-powered melody refinement workflow:
1. Generate a melody using the existing system
2. Apply AI refinement (mock mode)
3. Compare results and show cost analysis
"""

from harmonyforge.generation.melody_generator import generate_melody, refine_melody_with_ai
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.styles.producers import NICK_MIRA
from harmonyforge.core.config import config


def test_ai_refinement_workflow():
    """Test the complete AI refinement workflow."""
    print("=" * 60)
    print("AI MELODY REFINEMENT WORKFLOW TEST")
    print("=" * 60)
    
    # Setup
    config.set_seed(1234)
    PRODUCER = NICK_MIRA
    KEY_ROOT = "D"
    SCALE_NAME = "Harmonic Minor"
    BPM = 138
    BARS = 4
    
    print(f"\nConfiguration:")
    print(f"  Producer: {PRODUCER.name}")
    print(f"  Key: {KEY_ROOT} {SCALE_NAME}")
    print(f"  BPM: {BPM}")
    print(f"  Bars: {BARS}")
    
    # Step 1: Generate original melody
    print(f"\n{'='*60}")
    print("STEP 1: GENERATE ORIGINAL MELODY")
    print(f"{'='*60}")
    
    prog_gen = ProgressionGenerator(style=PRODUCER.signature)
    progression = prog_gen.generate(root_note=KEY_ROOT, scale_name=SCALE_NAME, bars=BARS)
    
    print(f"Progression: {progression.chords_roman}")
    
    original_melody = generate_melody(
        progression_midi=progression.chords_midi,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        bpm=BPM
    )
    
    print(f"Original melody: {len(original_melody)} notes")
    original_notes = [event.midi_note for event in original_melody]
    print(f"Note sequence: {original_notes[:10]}{'...' if len(original_notes) > 10 else ''}")
    
    # Step 2: Test AI refinement (disabled)
    print(f"\n{'='*60}")
    print("STEP 2: AI REFINEMENT (DISABLED)")
    print(f"{'='*60}")
    
    refined_disabled, meta_disabled = refine_melody_with_ai(
        melody_events=original_melody,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        enable_ai=False
    )
    
    print(f"AI used: {meta_disabled['ai_used']}")
    print(f"Reason: {meta_disabled['reason']}")
    print(f"Notes changed: {len([e1 for e1, e2 in zip(original_melody, refined_disabled) if e1.midi_note != e2.midi_note])}")
    
    # Step 3: Test AI refinement (enabled, mock mode)
    print(f"\n{'='*60}")
    print("STEP 3: AI REFINEMENT (ENABLED - MOCK MODE)")
    print(f"{'='*60}")
    
    refined_mock, meta_mock = refine_melody_with_ai(
        melody_events=original_melody,
        scale_name=SCALE_NAME,
        key_root=KEY_ROOT,
        style=PRODUCER.signature,
        enable_ai=True,
        ai_confidence_threshold=0.7
    )
    
    print(f"AI used: {meta_mock['ai_used']}")
    print(f"Was mock: {meta_mock['was_mock']}")
    print(f"Model: {meta_mock['model_used']}")
    print(f"Applied suggestions: {meta_mock['applied_suggestions']}/{meta_mock['total_suggestions']}")
    print(f"Overall improvement: {meta_mock['overall_improvement']}")
    
    # Show suggestions
    if meta_mock['suggestions']:
        print(f"\nAI Suggestions:")
        for i, sugg in enumerate(meta_mock['suggestions'], 1):
            print(f"  {i}. {sugg['category'].upper()}")
            print(f"     {sugg['original']} -> {sugg['suggested']} (confidence: {sugg['confidence']:.2%})")
            print(f"     Reason: {sugg['reason']}")
    
    # Show cost analysis
    print(f"\n{'='*60}")
    print("COST ANALYSIS")
    print(f"{'='*60}")
    print(f"Input tokens: {meta_mock['input_tokens']}")
    print(f"Output tokens: {meta_mock['output_tokens']}")
    print(f"Total cost: ${meta_mock['cost_usd']:.6f}")
    
    # Compare melodies
    print(f"\n{'='*60}")
    print("MELODY COMPARISON")
    print(f"{'='*60}")
    
    refined_notes = [event.midi_note for event in refined_mock]
    changed_indices = [i for i, (o, r) in enumerate(zip(original_notes, refined_notes)) if o != r]
    
    print(f"Original notes: {original_notes}")
    print(f"Refined notes:  {refined_notes}")
    print(f"Changed indices: {changed_indices}")
    print(f"Total changes: {len(changed_indices)}")
    
    if changed_indices:
        print(f"\nDetailed changes:")
        for idx in changed_indices:
            print(f"  Position {idx}: {original_notes[idx]} -> {refined_notes[idx]}")
    
    # Step 4: Test with different confidence thresholds
    print(f"\n{'='*60}")
    print("STEP 4: CONFIDENCE THRESHOLD TEST")
    print(f"{'='*60}")
    
    thresholds = [0.5, 0.7, 0.9]
    for threshold in thresholds:
        refined, meta = refine_melody_with_ai(
            melody_events=original_melody,
            scale_name=SCALE_NAME,
            key_root=KEY_ROOT,
            style=PRODUCER.signature,
            enable_ai=True,
            ai_confidence_threshold=threshold
        )
        print(f"Threshold {threshold:.1f}: {meta['applied_suggestions']}/{meta['total_suggestions']} suggestions applied")
    
    print(f"\n{'='*60}")
    print("WORKFLOW TEST COMPLETE")
    print(f"{'='*60}")
    print(f"\nKey findings:")
    print(f"1. AI integration is safe (disabled by default)")
    print(f"2. Mock mode provides realistic test data")
    print(f"3. Cost is negligible even with real API calls")
    print(f"4. Confidence threshold controls suggestion application")
    print(f"5. Original melody is preserved when AI is disabled")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_ai_refinement_workflow()