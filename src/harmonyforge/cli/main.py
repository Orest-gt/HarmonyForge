"""
HarmonyForge CLI v1.0.

Core command: `harmonyforge generate`
Experimental command: `harmonyforge arrange` (gated, requires arrangement engine)
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
from pathlib import Path

from harmonyforge.styles.genome import StyleSignature
from harmonyforge.core.config import config
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern

app = typer.Typer(
    help="HarmonyForge v1.0 — AI-assisted MIDI composition for professional producers.",
    no_args_is_help=True,
)
console = Console()


def _build_style(artist: str, producer: str, prompt: str) -> StyleSignature:

    producer_sig = get_producer(producer).signature

    artist_names = [a.strip() for a in artist.split(",")]
    if len(artist_names) > 1:
        base = get_artist(artist_names[0]).signature
        blend = get_artist(artist_names[1]).signature
        artist_sig = base.interpolate(blend, weight=0.5, non_linear=True)
        console.print(f"  Blending styles: [cyan]{artist_names[0]}[/cyan] + [cyan]{artist_names[1]}[/cyan]")
    else:
        artist_sig = get_artist(artist_names[0]).signature

    # Producer anchors the sound (70%), artist flavours it (30%)
    active = producer_sig.interpolate(artist_sig, weight=0.3, non_linear=True)

    if prompt:
        active = parse_prompt_to_signature(prompt, active)
        console.print(f"  Prompt applied: [italic]{prompt}[/italic]")

    return active


@app.command()
def generate(
    artist: str = typer.Option("Travis Scott", "--artist", "-a",
                               help="Artist to emulate. Comma-separate two for blending."),
    producer: str = typer.Option("Metro Boomin", "--producer", "-p",
                                 help="Producer to emulate."),
    key: str = typer.Option("C",     "--key",   "-k", help="Root key  (C  C#  D  Eb  E  F  F#  G  Ab  A  Bb  B)"),
    scale: str = typer.Option("minor", "--scale", "-s",
                               help="Scale  (minor | major | harmonic_minor | dorian | phrygian)"),
    bars: int = typer.Option(8,   "--bars", "-b", help="Loop length in bars (default 8)"),
    bpm: Optional[int] = typer.Option(None, "--bpm",         help="Override BPM (defaults to style)"),
    prompt: str = typer.Option("",   "--prompt",      help="Mood words  e.g. 'dark ambient sparse'"),
    seed: Optional[int] = typer.Option(None, "--seed",        help="Random seed for deterministic output"),
    out_dir: str = typer.Option("./output", "--out-dir", "-o", help="Output directory"),
) -> None:
    """Generate a set of MIDI stem loops ready for your DAW."""

    console.print(Panel.fit(
        f"[bold blue]HarmonyForge v1.0[/bold blue]\n"
        f"[white]{artist}[/white] x [white]{producer}[/white]  "
        f"[dim]|[/dim]  [yellow]{key} {scale}[/yellow]  "
        f"[dim]|[/dim]  {bars} bars",
        border_style="blue",
    ))

    # Seed
    if seed is not None:
        config.set_seed(seed)

    # Build style genome
    style = _build_style(artist, producer, prompt)

    # Override BPM if requested
    if bpm is not None:
        style = style.model_copy(update={})  # pydantic v2 copy

    # Generate core loop
    gen = ProgressionGenerator(style)
    prog = gen.generate(key, scale, bars)
    if bpm is not None:
        prog = prog.model_copy(update={"bpm": bpm})

    melody = generate_melody(prog.chords_midi, scale, key, style, prog.bpm)
    bass   = generate_808_pattern(prog.chords_midi, style, prog.bpm)

    # Export stems
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True, parents=True)

    from harmonyforge.midi.exporter import export_loop
    export_loop(prog, melody, bass, out_path, prog.bpm)

    # Summary table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[green]OK[/green]", "BPM",    str(prog.bpm))
    table.add_row("[green]OK[/green]", "Chords", " - ".join(prog.chords_roman))
    table.add_row("[green]OK[/green]", "Stems",  str(out_path.absolute()))

    console.print(table)
    console.print("\n[bold green]Done.[/bold green] Import the stems into your DAW.\n")


@app.command()
def arrange(
    artist: str  = typer.Option("Travis Scott", "--artist"),
    producer: str = typer.Option("Metro Boomin", "--producer"),
    key: str    = typer.Option("C",     "--key"),
    scale: str  = typer.Option("minor", "--scale"),
    bars: int   = typer.Option(64,      "--bars"),
    seed: Optional[int] = typer.Option(None, "--seed"),
    out_dir: str = typer.Option("./output", "--out-dir"),
) -> None:
    """[EXPERIMENTAL] Generate a full-length song arrangement (intro/verse/hook/outro)."""

    console.print("[yellow]⚠  arrange is experimental — output structure may change.[/yellow]\n")

    try:
        from harmonyforge.generation.arrangement_generator import generate_arrangement
        from harmonyforge.midi.exporter import export_arrangement
    except ImportError:
        console.print("[red]Arrangement engine not available.[/red]")
        raise typer.Exit(1)

    if seed is not None:
        config.set_seed(seed)

    style = _build_style(artist, producer, "")
    arrangement = generate_arrangement(key, scale, style, total_bars=bars)

    out_path = Path(out_dir)
    export_arrangement(arrangement, out_path)

    hook = next((s for s in arrangement.sections if "Hook" in s.name), arrangement.sections[0])
    console.print(f"[bold green]Done.[/bold green]  {len(arrangement.sections)} sections · "
                  f"{arrangement.bpm} BPM · Hook: {' – '.join(hook.progression.chords_roman)}")
    console.print(f"Exported to {out_path.absolute()}")


@app.command()
def info() -> None:
    """Show installed version and available artist/producer profiles."""
    from harmonyforge.styles.artists import ARTISTS
    from harmonyforge.styles.producers import PRODUCERS

    console.print("[bold blue]HarmonyForge v1.0[/bold blue]\n")
    console.print("[bold]Artists:[/bold]  " + "  ·  ".join(ARTISTS.keys()))
    console.print("[bold]Producers:[/bold] " + "  ·  ".join(PRODUCERS.keys()))


if __name__ == "__main__":
    app()
