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


def snap_to_16th(beat: float) -> float:
    """Snap beat positions to the nearest 16th note."""
    return round(beat * 4.0) / 4.0


def detect_resolution_window(current_beat: float, total_beats: float) -> float:
    """Return a magnetic strength factor near phrase/chord boundaries."""
    if total_beats <= 0:
        return 0.0

    beat_in_bar = current_beat % 4.0
    distance_to_boundary = min(beat_in_bar, 4.0 - beat_in_bar)

    if distance_to_boundary >= 1.0:
        return 0.0

    # Strength ramps linearly within one beat of a boundary
    return max(0.0, min(1.0, 1.0 - (distance_to_boundary / 1.0)))


class MelodyEvent(BaseModel):
    midi_note: int
    start_beat: float
    duration_beats: float
    velocity: int
    tension: float = 0.0  # Accumulated harmonic tension (gravity field potential)


def compute_harmonic_pull(
    pitch: int,
    chord_tones: List[int],
    style: StyleSignature,
    current_tension: float,
    distance_weight: float = 1.0
) -> float:
    """
    Computes gravitational pull from chord tones with style-aware dissonance handling.
    Closer chord tones pull harder, while tension and dark/dense contexts make
    harsh tritone or major-seventh clashes feel less attractive.
    """
    if not chord_tones:
        return 0.0

    nearest_chord = min(chord_tones, key=lambda c: abs(pitch - c))
    distance = abs(pitch - nearest_chord)

    gravitational_force = distance_weight / (1.0 + distance ** 2)

    root_pc = chord_tones[0] % 12
    note_pc = pitch % 12
    interval_to_root = min((note_pc - root_pc) % 12, (root_pc - note_pc) % 12)

    style_pressure = (
        0.2
        + 0.35 * style.darkness_level
        + 0.2 * style.rhythmic_density
        + 0.2 * (1.0 - style.dissonance_tolerance)
    )

    if interval_to_root in {6, 11}:
        penalty = 0.22 + 0.35 * style_pressure
        if interval_to_root == 11:
            penalty += 0.08
        gravitational_force *= max(0.05, 1.0 - penalty)

    net_pull = gravitational_force - (current_tension * (0.35 + 0.15 * style.rhythmic_density))
    return max(0.0, net_pull)


def select_weighted_pitch(
    prev_pitch: int,
    scale_notes: List[int],
    current_chord: List[int],
    style: StyleSignature,
    rng: random.Random,
    current_tension: float = 0.0,
    recent_pitches: List[int] | None = None,
) -> int:
    """
    Selects the next pitch with a producer-friendly balance of chord support,
    stepwise motion, and phrase shape. It leans toward connected motion and
    avoids stale repetitions or overly harsh clashes in dark, dense contexts.
    """
    if not scale_notes:
        return prev_pitch

    weights: List[float] = []
    chord_pcs = [c % 12 for c in current_chord]
    recent_window = list(recent_pitches or [])[-3:]

    for note in scale_notes:
        interval = abs(note - prev_pitch)
        note_pc = note % 12
        chord_clash_penalty = 1.0
        is_chord_tone = note % 12 in chord_pcs

        # Strongly discourage semitone clashes against the active chord.
        for chord_pc in chord_pcs:
            interval_to_chord = min((note_pc - chord_pc) % 12, (chord_pc - note_pc) % 12)
            if interval_to_chord == 1:
                clash_penalty = 0.03 if (style.darkness_level > 0.7 or current_tension > 0.5) else 0.08
                if style.darkness_level > 0.7 and current_tension > 0.45:
                    clash_penalty *= 0.5
                chord_clash_penalty *= clash_penalty
            elif interval_to_chord == 2:
                chord_clash_penalty *= 0.45
            elif interval_to_chord == 3:
                chord_clash_penalty *= 0.75

        # Base contour weights favor small, connected steps over random leaps.
        if interval == 0:
            repetition_penalty = 0.2 if (style.darkness_level > 0.7 and current_tension > 0.5) else 0.55
            if recent_window and len(recent_window) >= 2 and recent_window[-1] == prev_pitch and recent_window[-2] == prev_pitch:
                repetition_penalty *= 0.35
            if is_chord_tone and style.darkness_level > 0.75 and current_tension > 0.6:
                repetition_penalty *= 0.75
            w = 2.2 * max(0.2, style.repetition_tendency) * repetition_penalty
        elif 1 <= interval <= 2:
            step_weight = 9.2 + 1.4 * style.rhythmic_density + 1.2 * style.repetition_tendency
            if style.darkness_level > 0.7 and current_tension > 0.5 and is_chord_tone:
                step_weight *= 1.15
            w = step_weight
        elif 3 <= interval <= 4:
            w = 6.2 + 0.6 * style.rhythmic_density
        elif 5 <= interval <= 6:
            w = 3.2 + 0.25 * (1.0 - style.dissonance_tolerance)
        elif interval == 12:
            w = 1.0 * max(0.2, 1.0 - style.dissonance_tolerance)
        else:
            w = 0.35 * max(0.1, 1.0 - (interval / 24.0))

        if style.darkness_level > 0.75 and style.rhythmic_density > 0.7 and interval >= 3:
            w *= 0.35

        # Give a mild directional bias so the melody keeps a phrase shape.
        if recent_window and len(recent_window) >= 2:
            motion = recent_window[-1] - recent_window[-2]
            if motion > 0 and note > prev_pitch:
                w *= 1.15 + 0.1 * style.rhythmic_density
            elif motion < 0 and note < prev_pitch:
                w *= 1.15 + 0.1 * style.rhythmic_density
            elif abs(note - prev_pitch) <= 2:
                w *= 1.05
            else:
                w *= 0.95

        # Harmonic gravity field modification; chord tones are strong anchors,
        # but nearby passing tones still survive when they support the line.
        if is_chord_tone:
            harmonic_pull = compute_harmonic_pull(note, current_chord, style, current_tension)
            chord_tone_boost = 1.6 + harmonic_pull * 2.0
            if style.darkness_level > 0.7 and current_tension > 0.5:
                if interval <= 2:
                    chord_tone_boost *= 1.35
                else:
                    chord_tone_boost *= 0.85
            w *= chord_tone_boost
        else:
            passing_tone_boost = 1.05 if 1 <= interval <= 2 else 1.0
            tension_penalty = max(0.25, 1.0 - (0.28 * current_tension + 0.12 * style.darkness_level))
            w *= passing_tone_boost * tension_penalty
            if style.darkness_level > 0.7 and current_tension > 0.5:
                w *= 0.30

        # Strongly prefer the actual chord-tone set when the melody is near a chord change.
        if style.darkness_level > 0.4 and interval <= 2:
            if is_chord_tone:
                w *= 1.6
            else:
                w *= 0.5

        w *= chord_clash_penalty

        # Reduce big jumps in dark/dense contexts so the phrase stays singable.
        if interval >= 3:
            leap_penalty = 0.3 + 0.15 * style.darkness_level + 0.1 * style.rhythmic_density
            if style.darkness_level > 0.7 and style.rhythmic_density > 0.7:
                leap_penalty += 0.15
            w *= max(0.2, 1.0 - leap_penalty)

        # Suppress repeated stagnation and obvious two-note loops.
        if recent_window:
            if note == recent_window[-1]:
                w *= 0.6
            if len(recent_window) >= 2 and recent_window[-1] == note and recent_window[-2] == note:
                w *= 0.2
            if len(recent_window) >= 2 and recent_window[-1] != note and recent_window[-2] == note:
                w *= 0.85

        weights.append(max(0.01, w))

    return rng.choices(scale_notes, weights=weights)[0]


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

    # Strong pull resolves decisively to the nearest chord tone and avoids semitone clashes.
    if magnetic_strength >= 0.7:
        return nearest_anchor

    if abs(current_pitch - nearest_anchor) <= 2 and current_pitch % 12 not in chord_pcs:
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

        # Calculate root chord and chord-tone context for the block
        block_chord = progression_midi[block_start_bar] if block_start_bar < len(progression_midi) else progression_midi[-1]
        block_chord_pcs = [c % 12 for c in block_chord]
        matching_chord_tones = [n for n in scale_notes if n % 12 in block_chord_pcs]

        # Determine if the block should lean into chord tones or expressive passing motion
        block_tension = min(1.0, accumulated_tension / 24.0)
        chord_lock_factor = 0.55 + 0.35 * (1.0 - block_tension)

        # Pivot the motif around the strongest chord tone in the block
        if matching_chord_tones:
            pivot_pitch = min(matching_chord_tones, key=lambda n: abs(n - scale_notes[center_idx]))
        else:
            pivot_pitch = scale_notes[center_idx]
        pivot_idx = scale_notes.index(pivot_pitch)

        block_pitches: List[int] = []
        for i, base_pitch in enumerate(motif_pitches):
            base_idx = scale_notes.index(base_pitch)
            pitch_idx = base_idx

            if form == "A":
                pitch = scale_notes[pitch_idx]
            elif form == "A_prime":
                if i < int(num_notes * 0.7):
                    pitch = scale_notes[pitch_idx]
                else:
                    pitch = scale_notes[pitch_idx]
                    if matching_chord_tones and rng.random() < 0.85:
                        pitch = min(matching_chord_tones, key=lambda n: abs(pitch - n))
            else:
                # B phrase resolves toward the pivot by stepwise motion
                if i >= int(num_notes * 0.4):
                    step_down = int((i - int(num_notes * 0.4)) * 0.8)
                    resolution_idx = max(0, pivot_idx - step_down)
                    pitch = scale_notes[resolution_idx]
                else:
                    pitch = scale_notes[pitch_idx]

            # Gradually favor chord tones when tension is high
            if matching_chord_tones and pitch % 12 not in block_chord_pcs:
                if rng.random() < chord_lock_factor:
                    pitch = min(matching_chord_tones, key=lambda n: abs(pitch - n))

            # Avoid overly wide leaps for better melodic continuity
            if block_pitches:
                last_pitch = block_pitches[-1]
                interval = abs(pitch - last_pitch)
                if interval > 7:
                    direction = 1 if pitch > last_pitch else -1
                    pitch = last_pitch + direction * 7
                    pitch = max(60, min(84, pitch))

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
                current_chord_pcs = [c % 12 for c in block_chord]
                is_chord_tone = (pitch % 12) in current_chord_pcs

                if not is_chord_tone:
                    # Non-chord tones accumulate tension
                    nearest_chord_tone = min(block_chord, key=lambda c: abs(pitch - c))
                    tension_increment = abs(pitch - nearest_chord_tone) * dur
                    accumulated_tension += tension_increment
                else:
                    accumulated_tension *= 0.7  # Tension decay on chord tones

                # If the current note is not a chord tone, re-evaluate it with gravity selection
                prev_pitch = events[-1].midi_note if events else pitch
                if not is_chord_tone or (
                        len(events) >= 2
                        and events[-1].midi_note == events[-2].midi_note
                        and events[-1].midi_note == pitch
                ):
                    pitch = select_weighted_pitch(
                        prev_pitch,
                        scale_notes,
                        block_chord,
                        style,
                        rng,
                        accumulated_tension,
                        [e.midi_note for e in events[-2:]]
                    )
                    current_chord_pcs = [c % 12 for c in block_chord]
                    is_chord_tone = (pitch % 12) in current_chord_pcs

                # --- MAGNETIC COLLAPSE AT RESOLUTION WINDOWS ---
                magnetic_strength = detect_resolution_window(current_beat_snapped, 8.0)
                if magnetic_strength > 0.6 and not is_chord_tone:
                    pitch = magnetic_collapse(pitch, block_chord, scale_notes, magnetic_strength, rng)
                    accumulated_tension *= 0.5  # Tension release on collapse

                # --- BOUNDARY CLEAN-UP FOR CHORD CHANGES ---
                note_end = current_beat_snapped + dur * 0.9
                next_bar_start = math.ceil(current_beat_snapped / 4.0) * 4.0
                if note_end > next_bar_start and block_start_bar + 1 < len(progression_midi):
                    next_chord = progression_midi[block_start_bar + 1]
                    if pitch % 12 not in [c % 12 for c in next_chord]:
                        pitch = magnetic_collapse(pitch, next_chord, scale_notes, 0.95, rng)
                        accumulated_tension *= 0.4
                
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
