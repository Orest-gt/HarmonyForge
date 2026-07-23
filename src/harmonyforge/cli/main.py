"""
HarmonyForge CLI v2.1.0.

Commands:
  make     — natural language: `hf make "dark travis x metro f# 8 bars"`
  generate — explicit flags:   `hf generate --artist "Travis Scott" --producer "Metro Boomin" ...`
  arrange  — [EXPERIMENTAL] full song arrangement
  info     — show installed profiles
"""

import os
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box as rich_box
from typing import Optional, Sequence
from pathlib import Path

from harmonyforge.styles.genome import StyleSignature
from harmonyforge.core.config import config
from harmonyforge.styles.artists import get_artist
from harmonyforge.styles.producers import get_producer
from harmonyforge.ai.prompt_parser import parse_prompt_to_signature, _default_swing
from harmonyforge.generation.progression_generator import ProgressionGenerator
from harmonyforge.generation.melody_generator import generate_melody
from harmonyforge.generation.bass_generator import generate_808_pattern
from harmonyforge.generation.counter_melody import generate_counter_melody
from harmonyforge.generation.vocal_topline import generate_vocal_topline

app = typer.Typer(
    help=(
        "HarmonyForge v2.1.0 — AI-assisted MIDI composition for professional producers.\n\n"
        "Quickstart:  hf make \"dark travis x metro f# 8 bars\"\n"
        "Full control: hf generate --artist \"Travis Scott\" --producer \"Metro Boomin\" --key F# --scale harmonic_minor"
    ),
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _parse_root_prompt_args(args: Sequence[str]) -> tuple[str, Optional[int], str, bool, bool, bool, bool]:
    """Parse a freeform prompt plus a few simple options from the root CLI."""
    prompt_parts: list[str] = []
    seed: Optional[int] = None
    out_dir = "./output"
    open_folder = True
    counter = False
    vocal = False
    humanize = False
    i = 0
    while i < len(args):
        token = args[i]
        if token in {"--seed", "-s"} and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif token in {"--out-dir", "-o"} and i + 1 < len(args):
            out_dir = args[i + 1]
            i += 2
        elif token == "--no-open":
            open_folder = False
            i += 1
        elif token == "--open":
            open_folder = True
            i += 1
        elif token == "--counter":
            counter = True
            i += 1
        elif token == "--vocal":
            vocal = True
            i += 1
        elif token == "--humanize":
            humanize = True
            i += 1
        elif token.startswith("-"):
            i += 1
        else:
            prompt_parts.append(token)
            i += 1
    return " ".join(prompt_parts).strip(), seed, out_dir, open_folder, counter, vocal, humanize


def main(args: Optional[Sequence[str]] = None) -> None:
    """Dispatch the CLI: prompt-style root input or Typer subcommands."""
    argv = list(sys.argv[1:] if args is None else args)
    if argv and argv[0] == "--version":
        console.print("harmonyforge 2.1.0")
        return
    if argv and argv[0] not in {"make", "generate", "arrange", "info"} and not argv[0].startswith("-"):
        prompt, seed, out_dir, open_folder, counter, vocal, humanize = _parse_root_prompt_args(argv)
        if prompt:
            _run_make_command(
                query=prompt,
                seed=seed,
                out_dir=out_dir,
                open_folder=open_folder,
                counter=counter,
                vocal=vocal,
                humanize=humanize,
            )
            return

    command = typer.main.get_command(app)
    command.main(args=argv, prog_name="harmonyforge", standalone_mode=False)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _build_style_from_keys(
    producer_keys: list[str],
    artist_keys: list[str],
    mood_words: list[str],
) -> tuple[StyleSignature, str]:
    """
    Build a blended StyleSignature from resolved DB keys.
    - If two producers: blend them 50/50, then treat as producer side.
    - If producer + artist: producer anchors 70%, artist flavours 30%.
    - Mood words are applied last via ONTOLOGY shifts.
    """
    from harmonyforge.ai.prompt_parser import parse_prompt_to_signature

    # Resolve producer side
    if len(producer_keys) >= 2:
        sig_a = get_producer(producer_keys[0]).signature
        sig_b = get_producer(producer_keys[1]).signature
        producer_sig = sig_a.interpolate(sig_b, weight=0.5, non_linear=True)
        label = f"{get_producer(producer_keys[0]).name} x {get_producer(producer_keys[1]).name}"
    elif producer_keys:
        producer_sig = get_producer(producer_keys[0]).signature
        label = get_producer(producer_keys[0]).name
    else:
        producer_sig = StyleSignature()
        label = "Default"

    # Resolve artist side
    if artist_keys:
        artist_sig = get_artist(artist_keys[0]).signature
        active = producer_sig.interpolate(artist_sig, weight=0.3, non_linear=True)
        label = f"{get_artist(artist_keys[0]).name} x {label}"
    else:
        active = producer_sig

    # Apply mood words
    if mood_words:
        active = parse_prompt_to_signature(" ".join(mood_words), active)

    return active, label


def _build_style(artist: str, producer: str, prompt: str) -> StyleSignature:
    """Legacy helper used by `generate` command (flag-based)."""
    producer_sig = get_producer(producer).signature
    artist_names = [a.strip() for a in artist.split(",")]
    if len(artist_names) > 1:
        base  = get_artist(artist_names[0]).signature
        blend = get_artist(artist_names[1]).signature
        artist_sig = base.interpolate(blend, weight=0.5, non_linear=True)
        console.print(f"  Blending: [cyan]{artist_names[0]}[/cyan] + [cyan]{artist_names[1]}[/cyan]")
    else:
        artist_sig = get_artist(artist_names[0]).signature

    active = producer_sig.interpolate(artist_sig, weight=0.3, non_linear=True)
    if prompt:
        active = parse_prompt_to_signature(prompt, active)
        console.print(f"  Prompt applied: [italic]{prompt}[/italic]")
    return active


def _run_generation(
    style: StyleSignature,
    key: str,
    scale: str,
    bars: int,
    bpm_override: Optional[int],
    swing: str,
    counter: bool,
    vocal: bool,
    humanize: bool,
    out_path: Path,
    open_folder: bool,
) -> None:
    """Shared generation + export pipeline used by both `make` and `generate`."""
    from harmonyforge.midi.exporter import export_loop

    try:
        gen  = ProgressionGenerator(style)
        prog = gen.generate(key, scale, bars)
        if bpm_override:
            prog = prog.model_copy(update={"bpm": bpm_override})

        melody = generate_melody(prog.chords_midi, scale, key, style, prog.bpm)
        bass   = generate_808_pattern(prog.chords_midi, style, prog.bpm)
        counter_events = generate_counter_melody(melody, prog.chords_midi, scale, key, style, prog.bpm) if counter else None
        vocal_events   = generate_vocal_topline(prog.chords_midi, scale, key, style, prog.bpm) if vocal else None

        out_path.mkdir(exist_ok=True, parents=True)
        export_loop(
            progression=prog,
            melody=melody,
            bass=bass,
            out_dir=out_path,
            bpm=prog.bpm,
            counter_melody=counter_events,
            vocal_topline=vocal_events,
            swing_style=swing,
            humanize=humanize,
        )

        stems = ["stem_chords.mid", "stem_bass.mid", "stem_melody.mid"]
        if counter_events:
            stems.append("stem_counter_melody.mid")
        if vocal_events:
            stems.append("stem_vocal_topline.mid")

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[green]OK[/green]", "BPM",     str(prog.bpm))
        table.add_row("[green]OK[/green]", "Chords",  "  ".join(prog.chords_roman))
        table.add_row("[green]OK[/green]", "Scale",   f"{key} {scale}")
        table.add_row("[green]OK[/green]", "Swing",   swing)
        if humanize:
            table.add_row("[green]OK[/green]", "Humanize", "enabled")
        table.add_row("[green]OK[/green]", "Stems",   "  ".join(stems))
        table.add_row("[green]OK[/green]", "Folder",  str(out_path.resolve()))
        console.print(table)
        console.print("\n[bold green]Done.[/bold green] Import the stems into your DAW.\n")

        if open_folder:
            try:
                os.startfile(str(out_path.resolve()))   # Windows: opens Explorer
            except Exception:
                pass  # Non-Windows or permission error — silently skip
    except Exception as e:
        console.print(f"[bold red]Error during generation:[/bold red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# `make` — natural language command (the main UX entry point)
# ---------------------------------------------------------------------------


def _run_make_command(
    query: str,
    seed: Optional[int],
    out_dir: str,
    open_folder: bool,
    counter: bool = False,
    vocal: bool = False,
    humanize: bool = False,
) -> None:
    try:
        from harmonyforge.ai.prompt_parser import extract_structured_params

        if seed is not None:
            config.set_seed(seed)

        params = extract_structured_params(query)

        style, label = _build_style_from_keys(
            params["producers"], params["artists"], params["mood_words"]
        )
        swing = params["swing"] or _default_swing(style.darkness_level, style.rhythmic_density)

        import re
        slug = re.sub(r"[^\w\s]", "", query.lower())
        slug = re.sub(r"\s+", "_", slug.strip())[:40]
        out_path = Path(out_dir) / slug

        producers_display = "  +  ".join(
            get_producer(k).name for k in params["producers"]
        ) if params["producers"] else "[dim]none detected[/dim]"
        artists_display = "  +  ".join(
            get_artist(k).name for k in params["artists"]
        ) if params["artists"] else "[dim]none[/dim]"

        understood = Table(show_header=False, box=rich_box.SIMPLE, padding=(0, 1))
        understood.add_row("[dim]query[/dim]", f"[italic]{query}[/italic]")
        understood.add_row("[cyan]producers[/cyan]", producers_display)
        if params["artists"]:
            understood.add_row("[cyan]artists[/cyan]", artists_display)
        understood.add_row("[cyan]key / scale[/cyan]", f"{params['key']} {params['scale']}")
        understood.add_row("[cyan]BPM[/cyan]", str(params["bpm"]) if params["bpm"] else "[dim]auto from style[/dim]")
        understood.add_row("[cyan]bars[/cyan]", str(params["bars"]))
        understood.add_row("[cyan]swing[/cyan]", swing)
        if params["mood_words"]:
            understood.add_row("[cyan]mood[/cyan]", "  ".join(params["mood_words"]))
        counter_requested = counter or params["counter"]
        vocal_requested = vocal or params["vocal"]

        extras = []
        if counter_requested:
            extras.append("counter-melody")
        if vocal_requested:
            extras.append("vocal topline")
        if extras:
            understood.add_row("[cyan]extras[/cyan]", "  ".join(extras))

        console.print(Panel(understood, title=f"[bold blue]HarmonyForge  ·  {label}[/bold blue]", border_style="blue"))

        if not params["producers"] and not params["artists"]:
            from harmonyforge.styles.producers import PRODUCERS_DB
            from harmonyforge.styles.artists import ARTISTS_DB
            console.print(
                "[yellow]Tip:[/yellow] I didn't detect a producer or artist name. "
                "Try: [italic]\"travis x metro f# 8 bars\"[/italic]\n"
                "Available producers: " + "  ·  ".join(PRODUCERS_DB.keys()) + "\n"
                "Available artists: " + "  ·  ".join(ARTISTS_DB.keys())
            )

        _run_generation(
            style=style,
            key=params["key"],
            scale=params["scale"],
            bars=params["bars"],
            bpm_override=params["bpm"],
            swing=swing,
            counter=counter_requested,
            vocal=vocal_requested,
            humanize=humanize,
            out_path=out_path,
            open_folder=open_folder,
        )
    except KeyError as e:
        console.print(f"[bold red]Error:[/bold red] Unknown artist or producer: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def make(
    query: str = typer.Argument(
        ...,
        help=(
            "Describe what you want in plain language.\n"
            "Examples:\n"
            "  \"dark travis x metro f# 8 bars\"\n"
            "  \"tay keith x atl jacob d phrygian 163 bpm drill\"\n"
            "  \"emotional neo-soul mike dean c dorian 16 bars vocal fills\"\n"
            "  \"southside x metro evil bb minor 140 bpm\""
        ),
    ),
    seed: Optional[int] = typer.Option(None, "--seed", "-s", help="Random seed for reproducible output"),
    out_dir: str = typer.Option("./output", "--out-dir", "-o", help="Output directory"),
    open_folder: bool = typer.Option(True, "--open/--no-open", help="Auto-open output folder when done"),
    counter: bool = typer.Option(False, "--counter", help="Add counter-melody stem"),
    vocal: bool = typer.Option(False, "--vocal", help="Add singable vocal topline stem"),
    humanize: bool = typer.Option(False, "--humanize", help="Apply swing/humanization to exported stems"),
) -> None:
    """Generate stems from a natural-language description — no flags needed."""
    _run_make_command(query=query, seed=seed, out_dir=out_dir, open_folder=open_folder, counter=counter, vocal=vocal, humanize=humanize)


# ---------------------------------------------------------------------------
# `generate` — explicit flags (power users / scripting)
# ---------------------------------------------------------------------------

@app.command()
def generate(
    artist:   str          = typer.Option("Travis Scott",  "--artist",   "-a",  help="Artist name. Comma-separate two to blend."),
    producer: str          = typer.Option("Metro Boomin",  "--producer", "-p",  help="Producer name."),
    key:      str          = typer.Option("C",             "--key",      "-k",  help="Root key (C  C#  D  Eb  E  F  F#  G  Ab  A  Bb  B)"),
    scale:    str          = typer.Option("minor",         "--scale",    "-s",  help="Scale (minor | major | harmonic_minor | dorian | phrygian)"),
    bars:     int          = typer.Option(8,               "--bars",     "-b",  help="Loop length in bars"),
    bpm:      Optional[int]= typer.Option(None,            "--bpm",             help="Override BPM (auto from style if omitted)"),
    prompt:   str          = typer.Option("",              "--prompt",          help="Mood words e.g. 'dark ambient sparse'"),
    counter:  bool         = typer.Option(False,           "--counter",         help="Add counter-melody stem"),
    vocal:    bool         = typer.Option(False,           "--vocal",           help="Add singable vocal topline stem"),
    swing:    str          = typer.Option("straight",      "--swing",           help="Swing template (straight | trap_bounce | dilla_swing | drill_push | afro_triplet)"),
    humanize: bool         = typer.Option(False,           "--humanize",        help="Apply swing/humanization to exported stems"),
    seed:     Optional[int]= typer.Option(None,            "--seed",            help="Random seed for deterministic output"),
    out_dir:  str          = typer.Option("./output",      "--out-dir",  "-o",  help="Output directory"),
    open_folder: bool      = typer.Option(True,            "--open/--no-open",  help="Auto-open output folder when done"),
) -> None:
    """Generate MIDI stem loops with explicit flags (power users)."""

    if seed is not None:
        config.set_seed(seed)

    style = _build_style(artist, producer, prompt)

    console.print(Panel.fit(
        f"[bold blue]HarmonyForge v1.1[/bold blue]\n"
        f"[white]{artist}[/white] x [white]{producer}[/white]  "
        f"[dim]|[/dim]  [yellow]{key} {scale}[/yellow]  "
        f"[dim]|[/dim]  {bars} bars",
        border_style="blue",
    ))

    out_path = Path(out_dir)
    _run_generation(
        style=style, key=key, scale=scale, bars=bars, bpm_override=bpm,
        swing=swing, counter=counter, vocal=vocal, humanize=humanize,
        out_path=out_path, open_folder=open_folder,
    )


# ---------------------------------------------------------------------------
# `arrange` — experimental full song
# ---------------------------------------------------------------------------

@app.command()
def arrange(
    artist:   str          = typer.Option("Travis Scott", "--artist"),
    producer: str          = typer.Option("Metro Boomin", "--producer"),
    key:      str          = typer.Option("C",            "--key"),
    scale:    str          = typer.Option("minor",        "--scale"),
    bars:     int          = typer.Option(64,             "--bars"),
    seed:     Optional[int]= typer.Option(None,           "--seed"),
    out_dir:  str          = typer.Option("./output",     "--out-dir"),
) -> None:
    """[EXPERIMENTAL] Generate a full-length song arrangement (intro/verse/hook/outro)."""

    console.print("[yellow]arrange is experimental — output structure may change.[/yellow]\n")

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
    console.print(
        f"[bold green]Done.[/bold green]  {len(arrangement.sections)} sections  "
        f"{arrangement.bpm} BPM  Hook: {' - '.join(hook.progression.chords_roman)}"
    )
    console.print(f"Exported to {out_path.resolve()}")


# ---------------------------------------------------------------------------
# `info` — list available profiles
# ---------------------------------------------------------------------------

@app.command()
def info() -> None:
    """Show version, available producer and artist profiles."""
    from harmonyforge.styles.artists import ARTISTS
    from harmonyforge.styles.producers import PRODUCERS

    console.print("[bold blue]HarmonyForge v1.1[/bold blue]\n")

    p_table = Table(title="Producers", box=rich_box.SIMPLE, show_header=True)
    p_table.add_column("Key",  style="cyan", no_wrap=True)
    p_table.add_column("Name", style="white")
    p_table.add_column("Aliases")
    p_table.add_column("BPM range")
    for k, p in PRODUCERS.items():
        p_table.add_row(k, p.name, "  /  ".join(p.aliases or ["-"]),
                        f"{p.signature.preferred_bpm_range[0]}-{p.signature.preferred_bpm_range[1]}")
    console.print(p_table)

    a_table = Table(title="Artists", box=rich_box.SIMPLE, show_header=True)
    a_table.add_column("Key",  style="cyan", no_wrap=True)
    a_table.add_column("Name", style="white")
    a_table.add_column("Aliases")
    for k, a in ARTISTS.items():
        a_table.add_row(k, a.name, "  /  ".join(a.aliases or ["-"]))
    console.print(a_table)

    console.print("\nExample: [italic]hf make \"dark travis x metro f# 8 bars\"[/italic]")
    console.print("Example: [italic]hf make \"tay keith x atl jacob phrygian 163 bpm drill counter\"[/italic]")


if __name__ == "__main__":
    app()
