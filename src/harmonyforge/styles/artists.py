"""
Database of Artist profiles with their Music Genome signatures.
"""

from typing import Dict
from harmonyforge.styles.genome import ArtistProfile, StyleSignature

TRAVIS_SCOTT = ArtistProfile(
    name="Travis Scott",
    aliases=["La Flame", "Travis", "Cactus Jack", "Jake"],
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

DRAKE = ArtistProfile(
    name="Drake",
    aliases=["Champagne Papi", "Drizzy"],
    signature=StyleSignature(
        harmonic_complexity=0.55,
        dissonance_tolerance=0.45,
        modal_interchange_prob=0.25,
        secondary_dominant_prob=0.20,
        rhythmic_density=0.45,
        syncopation_level=0.40,
        repetition_tendency=0.70,
        melodic_range=14,
        darkness_level=0.55,
        tension_preference=0.65,
        preferred_scales=["minor", "dorian", "major"],
        preferred_chord_types=["min7", "maj7", "dom7", "sus4"],
        preferred_bpm_range=(95, 125)
    )
)

KENDRICK_LAMAR = ArtistProfile(
    name="Kendrick Lamar",
    aliases=["K.Dot"],
    signature=StyleSignature(
        harmonic_complexity=0.80,
        dissonance_tolerance=0.70,
        modal_interchange_prob=0.60,
        secondary_dominant_prob=0.30,
        rhythmic_density=0.65,
        syncopation_level=0.60,
        repetition_tendency=0.55,
        melodic_range=18,
        darkness_level=0.75,
        tension_preference=0.80,
        preferred_scales=["minor", "dorian", "mixolydian"],
        preferred_chord_types=["min7", "dom7", "maj7", "dim7", "sus2"],
        preferred_bpm_range=(80, 120)
    )
)

PLAYBOI_CARTI = ArtistProfile(
    name="Playboi Carti",
    aliases=["Carti"],
    signature=StyleSignature(
        harmonic_complexity=0.35,
        dissonance_tolerance=0.85,
        modal_interchange_prob=0.15,
        secondary_dominant_prob=0.10,
        rhythmic_density=0.70,
        syncopation_level=0.85,
        repetition_tendency=0.90,
        melodic_range=10,
        darkness_level=0.90,
        tension_preference=0.85,
        preferred_scales=["minor", "phrygian", "harmonic_minor"],
        preferred_chord_types=["min", "dim", "min7"],
        preferred_bpm_range=(140, 170)
    )
)

ARTISTS_DB: Dict[str, ArtistProfile] = {
    "travis_scott": TRAVIS_SCOTT,
    "future": FUTURE,
    "drake": DRAKE,
    "kendrick_lamar": KENDRICK_LAMAR,
    "playboi_carti": PLAYBOI_CARTI,
}

# Public alias used by the CLI info command
ARTISTS = ARTISTS_DB

def get_artist(name: str) -> ArtistProfile:
    clean_name = name.lower().replace(" ", "_")
    if clean_name in ARTISTS_DB:
        return ARTISTS_DB[clean_name]

    normalized_name = clean_name.strip("_")
    for profile in ARTISTS_DB.values():
        candidate_names = {profile.name.lower().replace(" ", "_")}
        candidate_names.update(alias.lower().replace(" ", "_") for alias in profile.aliases)
        if normalized_name in candidate_names:
            return profile

    # Fallback to default
    return ArtistProfile(name=name, signature=StyleSignature())
