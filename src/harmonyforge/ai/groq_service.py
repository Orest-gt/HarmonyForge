"""
Groq AI Service for HarmonyForge - Mock-First Implementation

This service provides AI-powered melody refinement with strict cost control:
- Mock-first: Returns predefined improvements without real API calls
- Dry-run mode: Toggle to run without AI
- Token efficiency: Small prompts (~50-100 tokens max)
- Cost monitoring: Show exact cost per operation
- Safety: No real API calls until explicitly enabled

Groq Pricing (Llama 3.1 8B):
- Input: $0.05 / 1M tokens
- Output: $0.08 / 1M tokens
"""

import os
import json
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Cost constants (per 1M tokens)
GROQ_INPUT_COST_PER_M = 0.05
GROQ_OUTPUT_COST_PER_M = 0.08


@dataclass
class TokenUsage:
    """Track token usage for cost monitoring."""
    input_tokens: int
    output_tokens: int
    
    @property
    def input_cost(self) -> float:
        """Calculate input cost in USD."""
        return (self.input_tokens / 1_000_000) * GROQ_INPUT_COST_PER_M
    
    @property
    def output_cost(self) -> float:
        """Calculate output cost in USD."""
        return (self.output_tokens / 1_000_000) * GROQ_OUTPUT_COST_PER_M
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost in USD."""
        return self.input_cost + self.output_cost


class MelodySuggestion(BaseModel):
    """AI suggestion for melody improvement."""
    original_note: int
    suggested_note: int
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str  # No length constraint to handle AI variations
    category: str = Field(default="harmonic")  # More flexible to handle AI variations


class AIResponse(BaseModel):
    """Response from AI melody refinement."""
    suggestions: List[MelodySuggestion]
    overall_improvement: str  # No length constraint
    token_usage: TokenUsage
    was_mock: bool = True
    model_used: str = "llama-3.1-8b-instant"


class GroqAIService:
    """
    Groq AI service with mock-first implementation.
    
    Configuration:
    - DRY_RUN_MODE: If True, always use mock responses
    - GROQ_API_KEY: Required for real API calls (not used in mock mode)
    """
    
    def __init__(self, dry_run: bool = True, api_key: Optional[str] = None):
        self.dry_run = dry_run
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self._mock_response_index = 0
        
        # Check if real API is enabled via environment variable
        env_enable_real = os.environ.get("GROQ_ENABLE_REAL_API", "False").lower() in ("true", "1", "yes")
        if env_enable_real and self.api_key:
            self.dry_run = False
        
    def refine_melody(
        self,
        melody_notes: List[int],
        scale_name: str,
        key_root: str,
        style_context: str = "trap"
    ) -> AIResponse:
        """
        Refine a melody using AI suggestions.
        
        Args:
            melody_notes: List of MIDI note numbers
            scale_name: Musical scale (e.g., "Harmonic Minor")
            key_root: Root note (e.g., "D")
            style_context: Musical style context
            
        Returns:
            AIResponse with suggestions and cost information
        """
        if self.dry_run:
            return self._mock_refine_melody(melody_notes, scale_name, key_root, style_context)
        else:
            return self._real_refine_melody(melody_notes, scale_name, key_root, style_context)
    
    def _mock_refine_melody(
        self,
        melody_notes: List[int],
        scale_name: str,
        key_root: str,
        style_context: str
    ) -> AIResponse:
        """
        Mock implementation - returns predefined improvements.
        
        This simulates AI behavior without real API calls.
        """
        # Simulate token usage (estimated for a ~50 token prompt)
        mock_input_tokens = 50
        mock_output_tokens = 30
        
        token_usage = TokenUsage(
            input_tokens=mock_input_tokens,
            output_tokens=mock_output_tokens
        )
        
        # Generate mock suggestions based on melody length
        suggestions = []
        num_suggestions = min(3, len(melody_notes))
        
        # Use a deterministic but varied pattern for mock suggestions
        for i in range(num_suggestions):
            note_idx = (i * 2) % len(melody_notes)
            original = melody_notes[note_idx]
            
            # Mock improvement logic: suggest chord tones or scale tones
            if i == 0:
                # First suggestion: improve harmonic fit
                suggested = original + 2 if original < 120 else original - 2
                confidence = 0.85
                reason = "Better chord tone fit"
                category = "harmonic"
            elif i == 1:
                # Second suggestion: rhythmic improvement
                suggested = original
                confidence = 0.72
                reason = "Add syncopation here"
                category = "rhythmic"
            else:
                # Third suggestion: motivic development
                suggested = original + 4 if original < 116 else original - 4
                confidence = 0.68
                reason = "Develop motif variation"
                category = "motivic"
            
            suggestions.append(MelodySuggestion(
                original_note=original,
                suggested_note=suggested,
                confidence=confidence,
                reason=reason,
                category=category
            ))
        
        return AIResponse(
            suggestions=suggestions,
            overall_improvement=f"Mock refinement for {len(melody_notes)} notes in {key_root} {scale_name}",
            token_usage=token_usage,
            was_mock=True,
            model_used="llama-3.1-8b-instant"
        )
    
    def _real_refine_melody(
        self,
        melody_notes: List[int],
        scale_name: str,
        key_root: str,
        style_context: str
    ) -> AIResponse:
        """
        Real implementation - calls Groq API.
        
        Uses Llama 3.1 8B for melody refinement suggestions.
        """
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "Groq package not installed. Install with: pip install groq"
            )
        
        if not self.api_key:
            raise ValueError(
                "API key required for real API calls. "
                "Set GROQ_API_KEY environment variable or pass api_key parameter."
            )
        
        # Create Groq client
        client = Groq(api_key=self.api_key)
        
        # Build efficient prompt (token-conscious)
        prompt = self._build_efficient_prompt(
            melody_notes, scale_name, key_root, style_context
        )
        
        try:
            # Call Groq API with Llama 3.1 8B Instant
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a melody refinement AI. Suggest improvements for musical melodies. Return JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200,  # Increased to avoid JSON validation errors
                response_format={"type": "json_object"}
            )
            
            # Extract token usage
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            token_usage = TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            # Parse response
            content = response.choices[0].message.content
            suggestions_data = json.loads(content)
            
            # Convert to MelodySuggestion objects
            suggestions = []
            for sugg in suggestions_data.get("suggestions", []):
                suggestions.append(MelodySuggestion(
                    original_note=sugg["original_note"],
                    suggested_note=sugg["suggested_note"],
                    confidence=sugg["confidence"],
                    reason=sugg["reason"],
                    category=sugg["category"]
                ))
            
            return AIResponse(
                suggestions=suggestions,
                overall_improvement=suggestions_data.get("overall_improvement", "AI-generated refinement"),
                token_usage=token_usage,
                was_mock=False,
                model_used="llama-3.1-8b-instant"
            )
            
        except Exception as e:
            # Fallback to mock on API error
            print(f"Groq API error: {e}. Falling back to mock mode.")
            import traceback
            traceback.print_exc()
            return self._mock_refine_melody(melody_notes, scale_name, key_root, style_context)
    
    def _build_efficient_prompt(
        self,
        melody_notes: List[int],
        scale_name: str,
        key_root: str,
        style_context: str
    ) -> str:
        """
        Build an efficient prompt that minimizes token usage.
        
        Target: ~50-100 tokens total
        """
        # Truncate melody if too long to save tokens
        max_notes = 12
        truncated_notes = melody_notes[:max_notes]
        
        notes_str = ",".join(map(str, truncated_notes))
        
        prompt = f"""Improve melody [{notes_str}]. Key: {key_root} {scale_name}. Style: {style_context}.

JSON: {{"suggestions": [{{"original_note":int,"suggested_note":int,"confidence":float,"reason":str,"category":"harmonic/rhythmic/motivic/phrasing"}}], "overall_improvement":str}}. Max 3 suggestions."""
        
        return prompt
    
    def estimate_cost(
        self,
        input_tokens: int,
        expected_output_tokens: int = 30
    ) -> Dict[str, float]:
        """
        Estimate cost for a given token usage.
        
        Args:
            input_tokens: Estimated input tokens
            expected_output_tokens: Expected output tokens
            
        Returns:
            Dictionary with cost breakdown
        """
        token_usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=expected_output_tokens
        )
        
        return {
            "input_cost_usd": token_usage.input_cost,
            "output_cost_usd": token_usage.output_cost,
            "total_cost_usd": token_usage.total_cost,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_tokens
        }
    
    def is_enabled(self) -> bool:
        """Check if real API calls are enabled."""
        return not self.dry_run and self.api_key is not None


# Global service instance (configured by default in dry-run mode)
_default_service: Optional[GroqAIService] = None


def get_groq_service(dry_run: bool = True, api_key: Optional[str] = None) -> GroqAIService:
    """
    Get or create the global Groq service instance.
    
    Args:
        dry_run: If True, use mock responses
        api_key: Optional API key (uses env var if not provided)
        
    Returns:
        GroqAIService instance
    """
    global _default_service
    
    if _default_service is None:
        _default_service = GroqAIService(dry_run=dry_run, api_key=api_key)
    
    return _default_service


def reset_service():
    """Reset the global service instance (useful for testing)."""
    global _default_service
    _default_service = None