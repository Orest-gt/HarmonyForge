"""
Validation Suite for V2.1.
Contains stress-testing capabilities (1000 generations) and
quality metric logging via the benchmark dataset.
"""

import json
import random
import time
from pathlib import Path
from typing import Dict, List

from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature
from harmonyforge.generation.arrangement_generator import generate_arrangement
from harmonyforge.analysis.evaluation import evaluate_progression


def stress_test(iterations: int = 1000) -> None:
    """
    Runs headless generations to verify 0% crash rate and valid internal logic.
    """
    print(f"Starting Stress Test: {iterations} generations...")
    keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]
    scales = ["minor", "major", "harmonic_minor", "dorian", "phrygian"]
    artists = ["Travis Scott", "Future", "Juice WRLD", "Drake"]

    success_count = 0
    start_time = time.time()

    for i in range(iterations):
        key = random.choice(keys)
        scale = random.choice(scales)
        artist = random.choice(artists)

        try:
            profile = get_artist(artist).signature
            # Headless generation (no file write)
            arrangement = generate_arrangement(key, scale, profile, total_bars=16)
            if arrangement.sections and len(arrangement.sections) > 0:
                success_count += 1
        except Exception as e:
            print(f"CRASH at iteration {i} ({artist}, {key} {scale}): {str(e)}")
            return

        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{iterations} ({success_count} successful)")

    elapsed = time.time() - start_time
    print(f"\nStress Test Complete! 0 crashes in {iterations} generations.")
    print(f"Time elapsed: {elapsed:.2f}s ({elapsed/iterations:.3f}s per song)")


def run_benchmark() -> None:
    """
    Runs the benchmark dataset and logs quality metrics.
    """
    json_path = Path(__file__).parent / "benchmark.json"
    with open(json_path, "r") as f:
        dataset = json.load(f)

    print(f"\nStarting Quality Benchmark ({len(dataset)} prompts)...")

    scores: Dict[str, List[float]] = {
        "musical_quality": [],
        "style_match": [],
        "originality": [],
        "emotion": [],
        "overall": []
    }

    for item in dataset:
        print(f"Benchmarking: {item['artist']} x {item['producer']} - {item['prompt']}")
        artist_sig = get_artist(item['artist']).signature
        prod_sig = get_producer(item['producer']).signature

        active_style = prod_sig.interpolate(artist_sig, weight=0.3)
        active_style = parse_prompt_to_signature(item['prompt'], active_style)

        arrangement = generate_arrangement(item['key'], item['scale'], active_style, total_bars=16)

        hook = arrangement.sections[0]
        eval_res = evaluate_progression(hook.progression.chords_midi, hook.progression.chords_roman, active_style)

        scores["musical_quality"].append(eval_res.musical_quality)
        scores["style_match"].append(eval_res.style_match)
        scores["originality"].append(eval_res.originality)
        scores["emotion"].append(eval_res.emotion)
        scores["overall"].append(eval_res.overall_score)

    n = len(dataset)
    print("\n--- BENCHMARK RESULTS ---")
    print(f"Avg Musical Quality:  {sum(scores['musical_quality'])/n:.3f}")
    print(f"Avg Style Match:      {sum(scores['style_match'])/n:.3f}")
    print(f"Avg Originality:      {sum(scores['originality'])/n:.3f}")
    print(f"Avg Emotion:          {sum(scores['emotion'])/n:.3f}")
    print(f"Avg OVERALL SCORE:    {sum(scores['overall'])/n:.3f} / 1.0")


if __name__ == "__main__":
    stress_test(iterations=100)  # Quick run for dev; full 1000 can be parameterized
    run_benchmark()
