"""
Test Groq AI Service - Mock-First Implementation

This demonstrates the mock-first approach with cost monitoring.
Run this to see the AI service in action without real API calls.
"""

from harmonyforge.ai.groq_service import GroqAIService, get_groq_service, reset_service


def test_mock_refinement():
    """Test the mock melody refinement."""
    print("=" * 60)
    print("GROQ AI SERVICE - MOCK MODE TEST")
    print("=" * 60)
    
    # Create service in dry-run mode (default)
    service = get_groq_service(dry_run=True)
    
    # Test melody (simple trap melody)
    melody_notes = [60, 63, 67, 65, 62, 66, 64, 68]
    scale_name = "Harmonic Minor"
    key_root = "D"
    style_context = "trap"
    
    print(f"\nInput melody: {melody_notes}")
    print(f"Scale: {key_root} {scale_name}")
    print(f"Style: {style_context}")
    print(f"\nService status:")
    print(f"  - Dry run mode: {service.dry_run}")
    print(f"  - API key set: {service.api_key is not None}")
    print(f"  - Real API enabled: {service.is_enabled()}")
    
    # Get AI suggestions
    print(f"\nCalling AI service...")
    response = service.refine_melody(
        melody_notes=melody_notes,
        scale_name=scale_name,
        key_root=key_root,
        style_context=style_context
    )
    
    # Display results
    print(f"\n{'='*60}")
    print("AI RESPONSE")
    print(f"{'='*60}")
    print(f"Model: {response.model_used}")
    print(f"Was mock: {response.was_mock}")
    print(f"Overall improvement: {response.overall_improvement}")
    print(f"Overall improvement: {response.overall_improvement}")
    
    print(f"\nSuggestions ({len(response.suggestions)}):")
    for i, suggestion in enumerate(response.suggestions, 1):
        print(f"\n  {i}. {suggestion.category.upper()} suggestion")
        print(f"     Original: {suggestion.original_note} -> Suggested: {suggestion.suggested_note}")
        print(f"     Confidence: {suggestion.confidence:.2%}")
        print(f"     Reason: {suggestion.reason}")
    
    print(f"\n{'='*60}")
    print("COST ANALYSIS")
    print(f"{'='*60}")
    print(f"Input tokens: {response.token_usage.input_tokens}")
    print(f"Output tokens: {response.token_usage.output_tokens}")
    print(f"Input cost: ${response.token_usage.input_cost:.6f}")
    print(f"Output cost: ${response.token_usage.output_cost:.6f}")
    print(f"Total cost: ${response.token_usage.total_cost:.6f}")
    
    # Show cost estimation for different scenarios
    print(f"\n{'='*60}")
    print("COST ESTIMATION FOR DIFFERENT OPERATIONS")
    print(f"{'='*60}")
    
    scenarios = [
        ("Single melody refinement", 50, 30),
        ("Full beat refinement", 200, 100),
        ("Batch of 10 refinements", 500, 300),
        ("Heavy usage (100 operations)", 5000, 3000),
    ]
    
    for name, input_toks, output_toks in scenarios:
        cost = service.estimate_cost(input_toks, output_toks)
        print(f"\n{name}:")
        print(f"  Input: {cost['input_tokens']} tokens (${cost['input_cost_usd']:.6f})")
        print(f"  Output: {cost['output_tokens']} tokens (${cost['output_cost_usd']:.6f})")
        print(f"  Total: ${cost['total_cost_usd']:.6f}")
    
    print(f"\n{'='*60}")
    print("GROQ PRICING REFERENCE")
    print(f"{'='*60}")
    print(f"Model: Llama 3.1 8B")
    print(f"Input: $0.05 / 1M tokens")
    print(f"Output: $0.08 / 1M tokens")
    print(f"\nKey insight: Even with 5000 tokens, cost is under $0.50")
    print(f"{'='*60}")


def test_cost_safety():
    """Demonstrate cost safety features."""
    print(f"\n{'='*60}")
    print("COST SAFETY TEST")
    print(f"{'='*60}")
    
    service = get_groq_service(dry_run=True)
    
    # Show that we can estimate costs before running
    print(f"\nEstimating costs before actual API calls:")
    print(f"1. Small operation (50 input, 30 output):")
    cost1 = service.estimate_cost(50, 30)
    print(f"   ${cost1['total_cost_usd']:.6f}")
    
    print(f"\n2. Medium operation (200 input, 100 output):")
    cost2 = service.estimate_cost(200, 100)
    print(f"   ${cost2['total_cost_usd']:.6f}")
    
    print(f"\n3. Large operation (1000 input, 500 output):")
    cost3 = service.estimate_cost(1000, 500)
    print(f"   ${cost3['total_cost_usd']:.6f}")
    
    print(f"\nSafety: All estimates available without API calls!")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_mock_refinement()
    test_cost_safety()
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"1. Review the mock responses and cost estimates")
    print(f"2. Enable real API calls by setting dry_run=False and providing API key")
    print(f"3. Integrate with melody_generator.py for actual refinement workflow")
    print(f"{'='*60}")