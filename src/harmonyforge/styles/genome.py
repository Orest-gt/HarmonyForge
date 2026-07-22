"""
Music Genome and Style Signature layer.
Defines the core aesthetic parameters for artists, producers, and genres.
"""

from pydantic import BaseModel, Field
from typing import List

class StyleSignature(BaseModel):
    """
    The Music Genome parameters defining a specific style.
    Values are typically normalized between 0.0 and 1.0.
    """
    # Harmonic Parameters
    harmonic_complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    dissonance_tolerance: float = Field(default=0.3, ge=0.0, le=1.0)
    modal_interchange_prob: float = Field(default=0.1, ge=0.0, le=1.0)
    secondary_dominant_prob: float = Field(default=0.1, ge=0.0, le=1.0)
    
    # Rhythmic Parameters
    rhythmic_density: float = Field(default=0.5, ge=0.0, le=1.0)
    syncopation_level: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Structural Parameters
    repetition_tendency: float = Field(default=0.8, ge=0.0, le=1.0)
    melodic_range: int = Field(default=12, description="Typical range in semitones")
    
    # Aesthetic / Emotional
    darkness_level: float = Field(default=0.5, ge=0.0, le=1.0)
    tension_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Preferred Palette
    preferred_scales: List[str] = Field(default_factory=list)
    preferred_chord_types: List[str] = Field(default_factory=list)
    preferred_bpm_range: tuple[int, int] = Field(default=(110, 140))
    
    def interpolate(self, other: 'StyleSignature', weight: float, non_linear: bool = True) -> 'StyleSignature':
        """
        Blends this signature with another. 
        weight: 0.0 means 100% self, 1.0 means 100% other.
        """
        import math
        def blend(v1: float, v2: float) -> float:
            if non_linear:
                # S-curve weight adjustment for more pronounced mixing boundaries
                w = 1 / (1 + math.exp(-10 * (weight - 0.5)))
                return (v1 * (1 - w)) + (v2 * w)
            return (v1 * (1 - weight)) + (v2 * weight)

        return StyleSignature(
            harmonic_complexity=blend(self.harmonic_complexity, other.harmonic_complexity),
            dissonance_tolerance=blend(self.dissonance_tolerance, other.dissonance_tolerance),
            modal_interchange_prob=blend(self.modal_interchange_prob, other.modal_interchange_prob),
            secondary_dominant_prob=blend(self.secondary_dominant_prob, other.secondary_dominant_prob),
            rhythmic_density=blend(self.rhythmic_density, other.rhythmic_density),
            syncopation_level=blend(self.syncopation_level, other.syncopation_level),
            repetition_tendency=blend(self.repetition_tendency, other.repetition_tendency),
            melodic_range=int(blend(self.melodic_range, other.melodic_range)),
            darkness_level=blend(self.darkness_level, other.darkness_level),
            tension_preference=blend(self.tension_preference, other.tension_preference),
            preferred_scales=list(set(self.preferred_scales + other.preferred_scales)),
            preferred_chord_types=list(set(self.preferred_chord_types + other.preferred_chord_types)),
            preferred_bpm_range=(
                int(blend(self.preferred_bpm_range[0], other.preferred_bpm_range[0])),
                int(blend(self.preferred_bpm_range[1], other.preferred_bpm_range[1]))
            )
        )

class ArtistProfile(BaseModel):
    """Profile for a specific artist."""
    name: str
    aliases: List[str] = Field(default_factory=list)
    signature: StyleSignature

class ProducerProfile(BaseModel):
    """Profile for a specific producer."""
    name: str
    aliases: List[str] = Field(default_factory=list)
    signature: StyleSignature

class GenreProfile(BaseModel):
    """Profile for a broad genre."""
    name: str
    signature: StyleSignature
