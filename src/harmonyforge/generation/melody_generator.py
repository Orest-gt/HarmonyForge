"""
Melody generator v1.3 — Harmonic Gravity Field Engine.

Key structural improvements for melodic cohesion:
  1. Directional Phrasing Wave: Uses continuous wave contour to generate organic arcs
     (Ascend -> Peak -> Descend) rather than random zig-zag motion.
  2. Strict Motif Preservation (A - A' - A - B):
     - Phrase A (Bars 1-2): Core motif theme.
     - Phrase A' (Bars 3-4): Preserves motif head (first 75% of notes), varies only the cadence tail.
     - Phrase A (Bars 5-6): Identical repetition of Phrase A to build instant hook memory.
     - Phrase B (Bars 7-8): Turnaround phrase resolving smoothly to tonic / chord tone.
  3. Harmonic Adaptation without Distortion: Transposes the motif by scale degrees to fit
     new chords rather than destroying internal pitch relationships with random downbeat snapping.
  4. Inverted Harmonic Gravity Field:
     - Background chords generate variable pull vectors
     - Non-chord tones accumulate kinetic tension over time
     - Phrase boundaries trigger magnetic collapse to anchor pitches
     - Melody naturally satisfies listener's psychological expectation
"""

import math
import random
from typing import List
from pydantic import BaseModel

from harmonyforge.core.config import config
from harmonyforge.styles.genome import StyleSignature
from harmonyforge.theory.scales import get_scale, get_notes_in_scale


class MelodyEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int
    tension: float = 0.0  # Accumulated harmonic tension (gravity field potential)


def compute_harmonic_pull(
    pitch: int,
    chord_tones: List[int],
    current_tension: float,
    distance_weight: float = 1.0
) -> float:
    """
    Computes gravitational pull from chord tones.
    Closer chord tones = stronger pull. Accumulated tension resists pull.
    """
    if not chord_tones:
        return 0.0
    
    # Find nearest chord tone
    nearest_chord = min(chord_tones, key=lambda c: abs(pitch - c))
    distance = abs(pitch - nearest_chord)
    
    # Gravitational pull: inverse square law with harmonic weighting
    gravitational_force = distance_weight / (1.0 + distance ** 2)
    
    # Tension resists gravitational pull
    net_pull = gravitational_force - (current_tension * 0.5)
    
    return max(0.0, net_pull)


def select_weighted_pitch(
    prev_pitch: int,
    scale_notes: List[int],
    current_chord: List[int],
    style: StyleSignature,
    rng: random.Random,
    current_tension: float = 0.0,
) -> int:
    """
    Selects the next pitch using harmonic gravity field.
    Pitch selection influenced by gravitational pull from chord tones and accumulated tension.
    """
    if not scale_notes:
        return prev_pitch

    weights: List[float] = []
    chord_pcs = [c % 12 for c in current_chord]

    for note in scale_notes:
        interval = abs(note - prev_pitch)
        
        # Base contour weights (preserves existing behavior)
        if interval == 0:
            w = 4.0 * style.repetition_tendency
        elif 1 <= interval <= 3:
            w = 8.0
        elif 4 <= interval <= 5:
            w = 4.0
        elif 6 <= interval <= 7:
            w = 2.5
        elif interval == 12:
            w = 3.5 * style.dissonance_tolerance
        else:
            w = 0.2 * max(0.1, 1.0 - (interval / 24.0))

        # Harmonic gravity field modification
        if note % 12 in chord_pcs:
            # Chord tones get harmonic pull boost
            harmonic_pull = compute_harmonic_pull(note, current_chord, current_tension)
            w *= (2.2 + harmonic_pull)
        else:
            # Non-chord tones get tension penalty
            w *= max(0.1, 1.0 - current_tension)

        weights.append(max(0.01, w))

    return rng.choices(scale_notes, weights=weights)[0]


def snap_to_16th(beat: float) -> float:
    """Quantizes beat position to nearest 16th-note grid (0.25 steps)."""
    return round(beat * 4.0) / 4.0


def detect_resolution_window(beat_position: float, phrase_length: float = 8.0) -> float:
    """
    Calculates magnetic pull strength based on structural position.
    Strongest near phrase boundaries and weaker toward the middle of the phrase.
    Returns strength in [0.0, 1.0].
    """
    normalized_beat = beat_position % phrase_length
    resolution_points = [0.0, phrase_length / 2.0, phrase_length]
    distance_to_resolution = min(abs(normalized_beat - point) for point in resolution_points)

    window_half_width = max(1.0, phrase_length / 8.0)
    magnetic_strength = 1.0 - (distance_to_resolution / window_half_width)
    return max(0.0, min(1.0, magnetic_strength))


def magnetic_collapse(
    current_pitch: int,
    target_chord: List[int],
    scale_notes: List[int],
    magnetic_strength: float,
    rng: random.Random,
) -> int:
    """
    Force trajectory collapse to the most contextually required anchor pitch.
    Stronger magnetic strength makes the melody resolve more decisively to the
    nearest chord tone, creating a convincing boundary cadence.
    """
    if magnetic_strength < 0.3:
        return current_pitch  # Not in resolution window

    chord_pcs = [c % 12 for c in target_chord]
    available_anchors = [n for n in scale_notes if n % 12 in chord_pcs]

    if not available_anchors:
        return current_pitch

    if current_pitch % 12 in chord_pcs:
        return current_pitch

    nearest_anchor = min(available_anchors, key=lambda n: abs(n - current_pitch))

    # Strong pull resolves decisively to the nearest chord tone.
    if magnetic_strength >= 0.7:
        return nearest_anchor

    distances = [abs(n - current_pitch) for n in available_anchors]
    weights = [1.0 / (1.0 + d) for d in distances]

    if rng.random() < magnetic_strength:
        return rng.choices(available_anchors, weights=weights)[0]

    return current_pitch


def _generate_phrase_arc(num_notes: int, rng: random.Random) -> List[float]:
    """
    Generates a smooth 2-bar melodic phrasing wave normalized in [0.0, 1.0].
    Uses a combination of sine arc and smooth gradient noise so notes follow an organic arch
    (rise -> peak -> gentle fall) instead of random zig-zag leaps.
    """
    arc: List[float] = []
    # Choose phrase shape type: Arch (rise-fall), Rise, or Fall-Rise
    shape_type = rng.choice(["arch", "arch", "rise_fall", "arch_decay"])

    for i in range(num_notes):
        t = i / max(1, num_notes - 1)  # Normalized time [0.0, 1.0]

        if shape_type == "arch":
            # Classic melodic arch: sin(pi * t)
            val = math.sin(math.pi * t)
        elif shape_type == "rise_fall":
            # Quick rise, slow fall
            val = math.sin(math.pi * (t ** 0.7))
        else:
            # Arch with subtle end decay
            val = math.sin(math.pi * t) * (1.0 - 0.2 * t)

        # Add subtle organic jitter (+/- 10%) so it doesn't sound synthesized/rigid
        jitter = rng.uniform(-0.10, 0.10)
        val = max(0.0, min(1.0, val + jitter))
        arc.append(val)

    return arc


def generate_melody(
    progression_midi: List[List[int]],
    scale_name: str,
    key_root: str,
    style: StyleSignature,
    bpm: int
) -> List[MelodyEvent]:
    """
    Generates a coherent, memorable lead melody with strict motif preservation,
    directional phrasing waves, and harmonic adaptation.
    """
    if config.seed is not None:
        rng = random.Random(config.seed)
    else:
        rng = random.Random()

    events: List[MelodyEvent] = []
    import music21.pitch
    root_midi = music21.pitch.Pitch(f"{key_root}4").midi

    scale = get_scale(scale_name)
    all_scale_notes = get_notes_in_scale(root_midi, scale, octaves=3)

    # Restrict melody range to a focused musical register (C4 to C6 / 60 to 84)
    scale_notes = [n for n in all_scale_notes if 60 <= n <= 84]
    if not scale_notes:
        scale_notes = [root_midi]
    
    # Initialize harmonic gravity field tracking
    accumulated_tension = 0.0

    # --- 1. GENERATE 2-BAR MOTIF RHYTHM & SKELETON ---
    motif_durations: List[float] = []
    beats_left = 8.0
    step_options = [0.25, 0.5, 1.0] if style.rhythmic_density > 0.5 else [0.5, 1.0, 2.0]

    while beats_left > 0:
        dur = rng.choice(step_options)
        if dur > beats_left:
            dur = beats_left
        motif_durations.append(dur)
        beats_left -= dur

    num_notes = len(motif_durations)

    # Rhythmic active mask (rests vs notes)
    active_mask = [rng.random() <= (0.30 + 0.60 * style.rhythmic_density) for _ in range(num_notes)]
    if not any(active_mask) and num_notes > 0:
        active_mask[0] = True

    # --- 2. GENERATE CORE MOTIF PITCHES USING DIRECTIONAL PHRASING ARC ---
    first_chord = progression_midi[0] if progression_midi else [root_midi]
    first_chord_pcs = [c % 12 for c in first_chord]
    chord_tones = [n for n in scale_notes if n % 12 in first_chord_pcs]

    # Start on a strong chord tone near center of range
    center_idx = len(scale_notes) // 2
    if chord_tones:
        anchor_pitch = min(chord_tones, key=lambda n: abs(n - scale_notes[center_idx]))
    else:
        anchor_pitch = scale_notes[center_idx]

    anchor_scale_idx = scale_notes.index(anchor_pitch)

    # Map phrasing wave to scale degree indices
    phrase_arc = _generate_phrase_arc(num_notes, rng)

    # Available scale degree range span for the motif (e.g. 5 to 9 scale steps wide)
    max_step_span = max(3, min(8, int(style.melodic_range // 2)))

    motif_pitches: List[int] = []
    for t_val in phrase_arc:
        # Scale step offset from anchor based on phrasing arc
        step_offset = int(round((t_val - 0.5) * 2.0 * max_step_span))
        target_idx = max(0, min(len(scale_notes) - 1, anchor_scale_idx + step_offset))
        motif_pitches.append(scale_notes[target_idx])

    # --- 3. GENERATE FULL PROGRESSION WITH STRICT FORM (A - A' - A - B) ---
    total_bars = len(progression_midi)
    two_bar_blocks = max(1, (total_bars + 1) // 2)

    for block_idx in range(two_bar_blocks):
        block_start_bar = block_idx * 2
        block_beat_offset = snap_to_16th(block_start_bar * 4.0)

        # Form assignment
        if block_idx == 0:
            form = "A"
        elif block_idx == 1:
            form = "A_prime"   # Variation on cadence tail
        elif block_idx == 2:
            form = "A"         # Exact repeat of Theme A (Hook memory!)
        else:
            form = "B"         # Cadential turnaround phrase

        # Calculate root chord tone shift for the block
        block_chord = progression_midi[block_start_bar] if block_start_bar < len(progression_midi) else progression_midi[-1]
        block_chord_pcs = [c % 12 for c in block_chord]

        # Shift the entire motif up/down by scale steps if underlying chord changes significantly
        head_pitch = motif_pitches[0]
        matching_chord_tones = [n for n in scale_notes if n % 12 in block_chord_pcs]
        if matching_chord_tones:
            shifted_head = min(matching_chord_tones, key=lambda n: abs(n - head_pitch))
            scale_shift = scale_notes.index(shifted_head) - scale_notes.index(head_pitch)
        else:
            scale_shift = 0

        # Build phrase pitches for this block
        block_pitches: List[int] = []
        for i, base_pitch in enumerate(motif_pitches):
            base_idx = scale_notes.index(base_pitch)
            shifted_idx = max(0, min(len(scale_notes) - 1, base_idx + scale_shift))

            if form == "A":
                # Exact motif
                pitch = scale_notes[shifted_idx]
            elif form == "A_prime":
                # Keep first 70% of notes IDENTICAL; vary only the cadence tail (last 30%)
                if i >= int(num_notes * 0.7):
                    # Tail variation: move to cadence chord tone
                    pitch = scale_notes[shifted_idx]
                    if matching_chord_tones:
                        pitch = min(matching_chord_tones, key=lambda n: abs(n - pitch))
                else:
                    pitch = scale_notes[shifted_idx]
            elif form == "B":
                # Turnaround B: inverse or descent toward tonic
                if i >= int(num_notes * 0.5):
                    # Stepwise descent to resolve
                    desc_idx = max(0, shifted_idx - (i - int(num_notes * 0.5) + 1))
                    pitch = scale_notes[desc_idx]
                else:
                    pitch = scale_notes[shifted_idx]

            block_pitches.append(pitch)

        # Place notes into events list
        current_beat = block_beat_offset
        for i, dur in enumerate(motif_durations):
            if i >= len(block_pitches):
                break

            current_beat_snapped = snap_to_16th(current_beat)

            if active_mask[i]:
                pitch = block_pitches[i]
                
                # --- HARMONIC GRAVITY FIELD TENSION TRACKING ---
                # Calculate distance from current chord
                current_chord_pcs = [c % 12 for c in block_chord]
                is_chord_tone = (pitch % 12) in current_chord_pcs
                
                if not is_chord_tone:
                    # Non-chord tones accumulate tension
                    nearest_chord_tone = min(block_chord, key=lambda c: abs(pitch - c))
                    tension_increment = abs(pitch - nearest_chord_tone) * dur
                    accumulated_tension += tension_increment
                else:
                    # Chord tones release tension
                    accumulated_tension *= 0.7  # Tension decay on chord tones
                
                # --- MAGNETIC COLLAPSE AT RESOLUTION WINDOWS ---
                magnetic_strength = detect_resolution_window(current_beat_snapped, 8.0)
                if magnetic_strength > 0.6 and not is_chord_tone:
                    # Force collapse to chord tone near phrase boundaries
                    pitch = magnetic_collapse(pitch, block_chord, scale_notes, magnetic_strength, rng)
                    accumulated_tension *= 0.5  # Tension release on collapse
                
                # --- ORGANIC PHRASING VELOCITY DYNAMICS (DYNAMIC BREATHING) ---
                # 1. Base velocity
                base_vel = 92
                
                # 2. Downbeat Accent (Beat 0.0 & Beat 2.0)
                is_downbeat = (current_beat_snapped % 2.0 == 0.0)
                if is_downbeat:
                    base_vel += rng.randint(8, 14)
                
                # 3. Off-beat 16th Ghost-note feel (steps 1 and 3)
                sixteenth_step = int(round(current_beat_snapped * 4.0)) % 4
                if sixteenth_step in [1, 3]:
                    base_vel -= rng.randint(10, 18)
                
                # 4. Melodic Peak Crescendo Boost
                if pitch == max(block_pitches):
                    base_vel += rng.randint(10, 16)
                
                # 5. Cadence Tail Decrescendo (last 2 notes of phrase)
                if i >= num_notes - 2:
                    base_vel -= rng.randint(8, 14)

                # Clamp velocity to valid MIDI range [40, 127]
                final_vel = max(40, min(127, base_vel + rng.randint(-4, 4)))

                events.append(MelodyEvent(
                    midi_note=pitch,
                    start_beat=current_beat_snapped,
                    duration_beats=dur * 0.9,
                    velocity=final_vel,
                    tension=accumulated_tension
                ))

            current_beat = snap_to_16th(current_beat + dur)

    return events
