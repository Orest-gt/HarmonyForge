"""
Database of Artist profiles with their Music Genome signatures.
"""

from typing import Dict
from harmonyforge.styles.genome import ArtistProfile, StyleSignature

TRAVIS_SCOTT = ArtistProfile(
    name="Travis Scott",
    aliases=["La Flame"],
    signature=StyleSignature(
        harmonic_complexity=0.7,
        dissonance_tolerance=0.75,
        modal_interchange_prob=0.5,
        secondary_dominant_prob=0.3,
        rhythmic_density=0.5,
        syncopation_level=0.7,
        repetition_tendency=0.6,
        melodic_range=16,
        darkness_level=0.8,
        tension_preference=0.85,
        preferred_scales=["minor", "harmonic_minor", "phrygian"],
        preferred_chord_types=["min", "min7", "maj7", "dim"],
        preferred_bpm_range=(130, 160)
    )
)

FUTURE = ArtistProfile(
    name="Future",
    aliases=["Pluto", "Hendrix"],
    signature=StyleSignature(
        harmonic_complexity=0.4,
        dissonance_tolerance=0.6,
        modal_interchange_prob=0.1,
        secondary_dominant_prob=0.1,
        rhythmic_density=0.6,
        syncopation_level=0.8,
        repetition_tendency=0.85,
        melodic_range=12,
        darkness_level=0.85,
        tension_preference=0.7,
        preferred_scales=["minor", "harmonic_minor"],
        preferred_chord_types=["min", "dim"],
        preferred_bpm_range=(140, 165)
    )
)

ARTISTS_DB: Dict[str, ArtistProfile] = {
    "travis_scott": TRAVIS_SCOTT,
    "future": FUTURE,
}

def get_artist(name: str) -> ArtistProfile:
    clean_name = name.lower().replace(" ", "_")
    if clean_name not in ARTISTS_DB:
        # Fallback to default
        return ArtistProfile(name=name, signature=StyleSignature())
    return ARTISTS_DB[clean_name]
