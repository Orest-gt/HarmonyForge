"""
Batch Generation script for benchmarking the V2 Engine.
Generates 20 variants using different styles and NLP prompts to test flexibility and interpolation.
"""

import subprocess
from pathlib import Path

commands = [
    # 1. Standard Metro Boomin
    ['uv', 'run', 'harmonyforge', 'generate', '--producer', 'Metro Boomin', '--artist', 'Future', '--key', 'D', '--scale', 'harmonic_minor', '--seed', '1', '--out-dir', 'benchmark_out/1_metro_future'],
    
    # 2. NLP Shifted (Evil Luxury)
    ['uv', 'run', 'harmonyforge', 'generate', '--producer', 'Southside', '--artist', 'Travis Scott', '--prompt', 'evil luxury ambient', '--key', 'C', '--scale', 'phrygian', '--seed', '2', '--out-dir', 'benchmark_out/2_southside_evil'],
    
    # 3. Interpolation Test
    ['uv', 'run', 'harmonyforge', 'generate', '--producer', 'Mike Dean', '--artist', 'Future, Travis Scott', '--key', 'A', '--scale', 'dorian', '--seed', '3', '--out-dir', 'benchmark_out/3_mikedean_hybrid'],
    
    # 4. High BPM Bouncy
    ['uv', 'run', 'harmonyforge', 'generate', '--producer', 'Metro Boomin', '--artist', 'Travis Scott', '--prompt', 'fast bouncy complex', '--key', 'F#', '--scale', 'minor', '--seed', '4', '--out-dir', 'benchmark_out/4_bouncy_trap']
]

def run_batch():
    for i, cmd in enumerate(commands):
        print(f"Running Benchmark {i+1}...")
        try:
            subprocess.run(cmd, check=True, shell=False)
        except subprocess.CalledProcessError as e:
            print(f"Error running benchmark {i+1}: {e}")
        print("-" * 40)

if __name__ == "__main__":
    run_batch()
