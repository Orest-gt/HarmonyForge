"""
MIDI Humanization.
Adds slight timing offsets and velocity variations.
"""

import random
import pretty_midi

def humanize_instrument(inst: pretty_midi.Instrument, timing_variance: float = 0.02, velocity_variance: int = 10) -> None:
    """
    Applies humanization to a pretty_midi instrument.
    timing_variance: max seconds to shift a note start/end.
    velocity_variance: max change in velocity.
    """
    for note in inst.notes:
        # Timing
        start_shift = random.uniform(-timing_variance, timing_variance)
        end_shift = random.uniform(-timing_variance, timing_variance)
        
        note.start = max(0.0, note.start + start_shift)
        note.end = max(note.start + 0.05, note.end + end_shift)
        
        # Velocity
        vel_shift = random.randint(-velocity_variance, velocity_variance)
        note.velocity = max(1, min(127, note.velocity + vel_shift))
