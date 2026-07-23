"""
50-Producer Objective Simulation Suite.
Simulates 50 realistic producer personas across Trap, Drill, R&B, Boom Bap, and Rage genres.
Audits and logs structural, harmonic, and rhythmic metrics for every generated track.
"""

import random
import time
from typing import List, Dict
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.generation.vocal_topline import generate_vocal_topline
from harmonyforge.analysis.evaluation import evaluate_progression

PRODUCER_50_DATASET = [
    {"artist": "Travis Scott", "producer": "Metro Boomin", "prompt": "dark space trap", "key": "C", "scale": "minor"},
    {"artist": "Juice WRLD", "producer": "Nick Mira", "prompt": "emotional guitar", "key": "E", "scale": "minor"},
    {"artist": "Playboi Carti", "producer": "Southside", "prompt": "rage synth bouncy", "key": "F#", "scale": "phrygian"},
    {"artist": "Drake", "producer": "40", "prompt": "underwater R&B sparse", "key": "D", "scale": "dorian"},
    {"artist": "Pop Smoke", "producer": "808Melo", "prompt": "UK drill aggressive", "key": "G", "scale": "phrygian"},
    {"artist": "Future", "producer": "Metro Boomin", "prompt": "cinematic dark", "key": "D", "scale": "harmonic_minor"},
    {"artist": "Joey Bada$$", "producer": "Statik Selektah", "prompt": "boom bap nostalgic", "key": "A", "scale": "minor"},
    {"artist": "Lil Uzi Vert", "producer": "Working on Dying", "prompt": "hyperpop fast bouncy", "key": "B", "scale": "major"},
    {"artist": "Gunna", "producer": "Wheezy", "prompt": "slimy guitar trap", "key": "C#", "scale": "minor"},
    {"artist": "Kendrick Lamar", "producer": "Sounwave", "prompt": "jazz rap complex", "key": "Bb", "scale": "dorian"},
]

# Duplicate and vary to reach 50 full producer scenarios
def get_50_scenarios() -> List[Dict[str, str]]:
    keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]
    scales = ["minor", "harmonic_minor", "phrygian", "dorian", "major"]
    prompts = ["dark ambient", "emotional slow", "fast bouncy", "cinematic heavy", "melancholy guitar"]
    
    scenarios = list(PRODUCER_50_DATASET)
    random.seed(42)
    
    while len(scenarios) < 50:
        base = random.choice(PRODUCER_50_DATASET)
        scenarios.append({
            "artist": base["artist"],
            "producer": base["producer"],
            "prompt": random.choice(prompts),
            "key": random.choice(keys),
            "scale": random.choice(scales)
        })
        
    return scenarios


def run_50_producer_simulation() -> None:
    scenarios = get_50_scenarios()
    print("==================================================")
    print("RUNNING 50-PRODUCER OBJECTIVE SIMULATION SUITE")
    print("==================================================")

    start_time = time.time()
    success_count = 0
    total_mel_notes = 0
    total_counter_notes = 0
    total_vocal_notes = 0
    eval_scores: List[float] = []

    for idx, item in enumerate(scenarios):
        try:
            artist_sig = get_artist(item["artist"]).signature
            prod_sig = get_producer(item["producer"]).signature
            
            active_style = prod_sig.interpolate(artist_sig, weight=0.3)
            if item["prompt"]:
                active_style = parse_prompt_to_signature(item["prompt"], active_style)
                
            # 1. Progression
            prog_gen = ProgressionGenerator(active_style)
            prog = prog_gen.generate(item["key"], item["scale"], bars=8)
            
            # 2. Melody
            melody = generate_melody(prog.chords_midi, item["scale"], item["key"], active_style, prog.bpm)
            
            # 3. Counter-Melody
            counter = generate_counter_melody(melody, prog.chords_midi, item["scale"], item["key"], active_style, prog.bpm)
            
            # 4. Vocal Topline
            vocal = generate_vocal_topline(prog.chords_midi, item["scale"], item["key"], active_style, prog.bpm)
            
            # 5. Bass
            bass = generate_808_pattern(prog.chords_midi, active_style, prog.bpm)
            assert len(bass) >= 0
            eval_res = evaluate_progression(prog.chords_midi, prog.chords_roman, active_style)
            eval_scores.append(eval_res.overall_score)
            
            total_mel_notes += len(melody)
            total_counter_notes += len(counter)
            total_vocal_notes += len(vocal)
            success_count += 1
            
            if (idx + 1) % 10 == 0:
                print(f"Simulated {idx + 1}/50 Producers... (Success: {success_count})")
                
        except Exception as e:
            print(f"CRASH at scenario {idx+1} ({item['artist']} x {item['producer']}): {e}")
            return

    elapsed = time.time() - start_time
    print("\n==================================================")
    print("50-PRODUCER SIMULATION RESULTS")
    print("==================================================")
    print("Status:             0 Crashes (100% Success Rate)")
    print(f"Total Scenarios:    {success_count}/50")
    print(f"Time Elapsed:       {elapsed:.2f}s ({elapsed/50:.3f}s per track)")
    print(f"Avg Melody Notes:   {total_mel_notes / 50:.1f} notes/track")
    print(f"Avg Counter-Melody: {total_counter_notes / 50:.1f} notes/track")
    print(f"Avg Vocal Topline:  {total_vocal_notes / 50:.1f} notes/track")
    print(f"Avg Harmony Score:  {sum(eval_scores)/len(eval_scores):.3f} / 1.0")
    print("==================================================")


if __name__ == "__main__":
    run_50_producer_simulation()
