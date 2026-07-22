"""
HarmonyForge CLI V2.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from pathlib import Path

from harmonyforge.core.config import config
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature
from harmonyforge.generation.arrangement_generator import generate_arrangement
from harmonyforge.analysis.evaluation import evaluate_progression
from harmonyforge.midi.exporter import export_arrangement

app = typer.Typer(help="HarmonyForge V2: AI-assisted music generation engine.")
console = Console()

@app.command()
def generate(
    prompt: str = typer.Option("", help="NLP prompt for stylistic shifts (e.g. 'evil bounce')"),
    artist: str = typer.Option("Travis Scott", help="Artist style to emulate (can be comma separated for blending)"),
    producer: str = typer.Option("Metro Boomin", help="Producer style to emulate"),
    key: str = typer.Option("C", help="Root key (e.g. C, F#, Ab)"),
    scale: str = typer.Option("minor", help="Scale type (e.g. minor, harmonic_minor)"),
    bars: int = typer.Option(64, help="Total arrangement length in bars"),
    seed: Optional[int] = typer.Option(None, help="Deterministic random seed"),
    out_dir: str = typer.Option("./output", help="Output directory for MIDI files")
) -> None:
    """Generates a full song arrangement based on input parameters."""
    console.print(Panel.fit(f"[bold blue]HarmonyForge V2 Engine[/bold blue]\nGenerating for: {artist} x {producer} in {key} {scale}\nPrompt: '{prompt}'"))
    
    if seed is not None:
        try:
            import torch
            torch.manual_seed(seed)
        except ImportError:
            config.set_seed(seed)
        
    producer_profile = get_producer(producer).signature
    
    # Handle artist blending if comma separated
    artist_names = [a.strip() for a in artist.split(",")]
    if len(artist_names) > 1:
        base_artist = get_artist(artist_names[0]).signature
        blend_artist = get_artist(artist_names[1]).signature
        artist_profile = base_artist.interpolate(blend_artist, weight=0.5, non_linear=True)
        console.print(f"Interpolating styles: {artist_names[0]} x {artist_names[1]}")
    else:
        artist_profile = get_artist(artist).signature
        
    # Hybrid blend: producer sets the primary groove, artist adds flavor
    active_style = producer_profile.interpolate(artist_profile, weight=0.3, non_linear=True)
    
    # NLP parser modifications
    if prompt:
        active_style = parse_prompt_to_signature(prompt, active_style)
        
    # Generate full arrangement
    arrangement = generate_arrangement(key, scale, active_style, total_bars=bars)
    
    # Evaluation (evaluate the core hook progression)
    hook_section = next((s for s in arrangement.sections if "Hook" in s.name), arrangement.sections[0])
    eval_res = evaluate_progression(hook_section.progression.chords_midi, hook_section.progression.chords_roman, active_style)
    
    # Export
    out_path = Path(out_dir)
    export_arrangement(arrangement, out_path)
    
    console.print(f"[bold green]Success![/bold green] Generated {bars} bars at {arrangement.bpm} BPM.")
    console.print(f"Hook Chords: {' - '.join(hook_section.progression.chords_roman)}")
    console.print(f"Evaluation (Quality/Style/Originality/Emotion): {eval_res.musical_quality:.2f} / {eval_res.style_match:.2f} / {eval_res.originality:.2f} / {eval_res.emotion:.2f}")
    console.print(f"Overall Score: {eval_res.overall_score:.2f}/1.0")
    console.print(f"Exported stems and metadata to {out_path.absolute()}")

@app.command()
def info() -> None:
    """Displays information about HarmonyForge."""
    console.print("[bold blue]HarmonyForge V2[/bold blue]")

if __name__ == "__main__":
    app()
