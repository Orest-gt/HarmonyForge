"""
Database of Producer profiles with their Music Genome signatures.
"""

from typing import Dict
from harmonyforge.styles.genome import ProducerProfile, StyleSignature

METRO_BOOMIN = ProducerProfile(
    name="Metro Boomin",
    aliases=["Metro"],
    signature=StyleSignature(
        harmonic_complexity=0.5,
        dissonance_tolerance=0.7,
        modal_interchange_prob=0.2,
        secondary_dominant_prob=0.1,
        rhythmic_density=0.6,
        syncopation_level=0.8,
        repetition_tendency=0.8,
        melodic_range=14,
        darkness_level=0.9,
        tension_preference=0.85,
        preferred_scales=["harmonic_minor", "phrygian", "minor", "phrygian_dominant"],
        preferred_chord_types=["min", "min7", "dim", "maj7"],
        preferred_bpm_range=(130, 165)
    )
)

SOUTHSIDE = ProducerProfile(
    name="Southside",
    aliases=["Sizzle", "808 Mafia"],
    signature=StyleSignature(
        harmonic_complexity=0.3,
        dissonance_tolerance=0.8,
        modal_interchange_prob=0.1,
        secondary_dominant_prob=0.05,
        rhythmic_density=0.4,
        syncopation_level=0.9,
        repetition_tendency=0.9,
        melodic_range=12,
        darkness_level=0.95,
        tension_preference=0.9,
        preferred_scales=["harmonic_minor", "minor"],
        preferred_chord_types=["min", "dim"],
        preferred_bpm_range=(140, 175)
    )
)

MIKE_DEAN = ProducerProfile(
    name="Mike Dean",
    signature=StyleSignature(
        harmonic_complexity=0.9,
        dissonance_tolerance=0.8,
        modal_interchange_prob=0.7,
        secondary_dominant_prob=0.6,
        rhythmic_density=0.7,
        syncopation_level=0.5,
        repetition_tendency=0.4,
        melodic_range=24,
        darkness_level=0.7,
        tension_preference=0.9,
        preferred_scales=["minor", "dorian", "lydian"],
        preferred_chord_types=["min9", "maj9", "dom7", "dim7", "sus4", "aug7"],
        preferred_bpm_range=(110, 140)
    )
)

ATL_JACOB = ProducerProfile(
    name="ATL Jacob",
    aliases=["Jacob Luttrell", "ATL"],
    signature=StyleSignature(
        # Rich, melodic trap — Drake "Rich Flex", 21 Savage, Future collab palette
        harmonic_complexity=0.75,
        dissonance_tolerance=0.55,
        modal_interchange_prob=0.35,   # Borrowing from parallel major (Neo-Soul touch)
        secondary_dominant_prob=0.25,
        rhythmic_density=0.55,
        syncopation_level=0.65,
        repetition_tendency=0.65,
        melodic_range=18,
        darkness_level=0.65,           # Dark but melodically warm — not pitch-black
        tension_preference=0.70,
        preferred_scales=["minor", "harmonic_minor", "dorian"],
        preferred_chord_types=["min7", "maj7", "min9", "dom7"],
        preferred_bpm_range=(130, 148)
    )
)

TAY_KEITH = ProducerProfile(
    name="Tay Keith",
    aliases=["Tay Keith FUNK", "Keith James"],
    signature=StyleSignature(
        # Memphis drill aggression — Look Alive, Sicko Mode, Bounce Out With That
        harmonic_complexity=0.30,      # Sparse melodies, raw chords
        dissonance_tolerance=0.80,     # Menacing tension baked in
        modal_interchange_prob=0.10,
        secondary_dominant_prob=0.05,
        rhythmic_density=0.85,         # Very dense, punchy — classic Memphis energy
        syncopation_level=0.88,        # Off-beat kicks, staggered hi-hats
        repetition_tendency=0.78,
        melodic_range=10,              # Tight, aggressive range
        darkness_level=0.92,
        tension_preference=0.92,
        preferred_scales=["minor", "phrygian"],   # Phrygian b2 = menace
        preferred_chord_types=["min", "dim", "min7"],
        preferred_bpm_range=(148, 172)
    )
)

PRODUCERS_DB: Dict[str, ProducerProfile] = {
    "metro_boomin": METRO_BOOMIN,
    "southside": SOUTHSIDE,
    "mike_dean": MIKE_DEAN,
    "atl_jacob": ATL_JACOB,
    "tay_keith": TAY_KEITH,
    # Can be extended massively
}

# Public alias used by the CLI info command
PRODUCERS = PRODUCERS_DB

def get_producer(name: str) -> ProducerProfile:
    clean_name = name.lower().replace(" ", "_")
    if clean_name not in PRODUCERS_DB:
        # Fallback to default
        return ProducerProfile(name=name, signature=StyleSignature())
    return PRODUCERS_DB[clean_name]
