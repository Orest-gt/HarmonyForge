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

NICK_MIRA = ProducerProfile(
    name="Nick Mira",
    aliases=["Nick Mira", "Internet Money"],
    signature=StyleSignature(
        # Dark, melodic trap — Juice WRLD, Lil Tecca, emotional piano leads
        harmonic_complexity=0.65,      # Rich, emotional harmonies
        dissonance_tolerance=0.60,     # Emotional tension but not too harsh
        modal_interchange_prob=0.40,   # Frequent borrowed chords for emotion
        secondary_dominant_prob=0.20,
        rhythmic_density=0.50,         # Melodic focus, not overly busy
        syncopation_level=0.55,        # Groovy but not aggressive
        repetition_tendency=0.70,      # Catchy, repetitive motifs
        melodic_range=16,              # Strong melodic range for emotional leads
        darkness_level=0.85,           # Dark, moody atmosphere
        tension_preference=0.75,       # Emotional tension without being overwhelming
        preferred_scales=["harmonic_minor", "minor", "phrygian"],  # Dark, emotional scales
        preferred_chord_types=["min7", "maj7", "min", "dim7"],  # Emotional chord qualities
        preferred_bpm_range=(135, 155)  # Classic trap tempo range
    )
)

FORTY = ProducerProfile(
    name="40",
    aliases=["Noah Shebib"],
    signature=StyleSignature(
        harmonic_complexity=0.60,
        dissonance_tolerance=0.35,
        modal_interchange_prob=0.30,
        secondary_dominant_prob=0.25,
        rhythmic_density=0.40,
        syncopation_level=0.35,
        repetition_tendency=0.75,
        melodic_range=13,
        darkness_level=0.45,
        tension_preference=0.55,
        preferred_scales=["minor", "dorian", "major"],
        preferred_chord_types=["min7", "maj7", "sus2", "sus4"],
        preferred_bpm_range=(90, 125)
    )
)

WHEEZY = ProducerProfile(
    name="Wheezy",
    aliases=["WheezyBeatz"],
    signature=StyleSignature(
        harmonic_complexity=0.40,
        dissonance_tolerance=0.80,
        modal_interchange_prob=0.20,
        secondary_dominant_prob=0.10,
        rhythmic_density=0.55,
        syncopation_level=0.80,
        repetition_tendency=0.85,
        melodic_range=11,
        darkness_level=0.90,
        tension_preference=0.80,
        preferred_scales=["minor", "harmonic_minor", "phrygian"],
        preferred_chord_types=["min", "dim", "min7"],
        preferred_bpm_range=(130, 170)
    )
)

BOI_1DA = ProducerProfile(
    name="Boi-1da",
    aliases=["Boi1da"],
    signature=StyleSignature(
        harmonic_complexity=0.70,
        dissonance_tolerance=0.60,
        modal_interchange_prob=0.45,
        secondary_dominant_prob=0.30,
        rhythmic_density=0.60,
        syncopation_level=0.55,
        repetition_tendency=0.65,
        melodic_range=15,
        darkness_level=0.60,
        tension_preference=0.70,
        preferred_scales=["minor", "major", "dorian"],
        preferred_chord_types=["min7", "maj7", "dom7", "sus4"],
        preferred_bpm_range=(100, 140)
    )
)

HIT_BOY = ProducerProfile(
    name="Hit-Boy",
    aliases=["Hit Boy"],
    signature=StyleSignature(
        harmonic_complexity=0.65,
        dissonance_tolerance=0.65,
        modal_interchange_prob=0.35,
        secondary_dominant_prob=0.20,
        rhythmic_density=0.50,
        syncopation_level=0.65,
        repetition_tendency=0.60,
        melodic_range=14,
        darkness_level=0.70,
        tension_preference=0.75,
        preferred_scales=["minor", "major", "mixolydian"],
        preferred_chord_types=["min7", "maj7", "dom7", "sus2"],
        preferred_bpm_range=(110, 150)
    )
)

PRODUCERS_DB: Dict[str, ProducerProfile] = {
    "metro_boomin": METRO_BOOMIN,
    "southside": SOUTHSIDE,
    "mike_dean": MIKE_DEAN,
    "atl_jacob": ATL_JACOB,
    "tay_keith": TAY_KEITH,
    "nick_mira": NICK_MIRA,
    "40": FORTY,
    "wheezy": WHEEZY,
    "boi-1da": BOI_1DA,
    "hit-boy": HIT_BOY,
    # Can be extended massively
}

# Public alias used by the CLI info command
PRODUCERS = PRODUCERS_DB

def get_producer(name: str) -> ProducerProfile:
    clean_name = name.lower().replace(" ", "_")
    if clean_name in PRODUCERS_DB:
        return PRODUCERS_DB[clean_name]

    normalized_name = clean_name.strip("_")
    for profile in PRODUCERS_DB.values():
        candidate_names = {profile.name.lower().replace(" ", "_")}
        candidate_names.update(alias.lower().replace(" ", "_") for alias in profile.aliases)
        if normalized_name in candidate_names:
            return profile

    # Fallback to default
    return ProducerProfile(name=name, signature=StyleSignature())
