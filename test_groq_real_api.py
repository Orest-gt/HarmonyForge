"""
Test Real Groq API Integration

This tests the actual Groq API with real API calls.
Set GROQ_ENABLE_REAL_API=True in .env to enable real API calls.
"""

import os
from dotenv import load_dotenv
from harmonyforge.ai.groq_service import get_groq_service, reset_service

# Load environment variables
load_dotenv()


def test_real_api_integration():
    """Test real Groq API integration."""
    print("=" * 60)
    print("REAL GROQ API INTEGRATION TEST")
    print("=" * 60)
    
    # Check configuration
    api_key = os.environ.get("GROQ_API_KEY")
    enable_real = os.environ.get("GROQ_ENABLE_REAL_API", "False").lower() in ("true", "1", "yes")
    
    print(f"\nConfiguration:")
    print(f"  API Key set: {bool(api_key)}")
    print(f"  Real API enabled: {enable_real}")
    
    if not api_key:
        print(f"\nERROR: GROQ_API_KEY not set in environment")
        print(f"Please set it in .env file or environment variables")
        return
    
    if not enable_real:
        print(f"\nNOTE: Real API calls are disabled")
        print(f"Set GROQ_ENABLE_REAL_API=True in .env to enable")
        print(f"\nFalling back to mock mode test...")
    
    # Create service (will use real API if enabled)
    service = get_groq_service(dry_run=not enable_real, api_key=api_key)
    
    print(f"\nService status:")
    print(f"  Dry run mode: {service.dry_run}")
    print(f"  API key set: {bool(service.api_key)}")
    print(f"  Real API enabled: {service.is_enabled()}")
    
    # Test melody
    melody_notes = [60, 63, 67, 65, 62, 66, 64, 68]
    scale_name = "Harmonic Minor"
    key_root = "D"
    style_context = "trap"
    
    print(f"\nInput melody: {melody_notes}")
    print(f"Scale: {key_root} {scale_name}")
    print(f"Style: {style_context}")
    
    # Get AI suggestions
    print(f"\nCalling AI service...")
    print(f"Mode: {'REAL API' if service.is_enabled() else 'MOCK'}")
    
    try:
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
        
        if service.is_enabled():
            print(f"\n[SUCCESS] Real API call successful!")
        else:
            print(f"\n[SUCCESS] Mock mode successful (enable real API for live calls)")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_real_api_integration()