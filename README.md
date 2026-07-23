# HarmonyForge v2.1.0

![HarmonyForge](https://img.shields.io/badge/HarmonyForge-v2.1.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

HarmonyForge is a next-generation AI-assisted harmony, melody, and MIDI generation engine designed for modern music producers. 

It is NOT a random chord generator. It is an aesthetic engine that models producer styles mathematically using a **Music Genome**, generates full 64-bar arrangements with energy automation, and features a functional **Evaluation Engine** and **Audio Intelligence**.

---

## 🚀 Features

- **Music Genome Interpolation:** Blend styles mathematically. Want 70% Juice WRLD and 30% Metro Boomin? HarmonyForge handles the tension, syncopation, and darkness mapping.
- **NLP Prompt Parser:** Use natural language (`--prompt "evil luxury cinematic"`) to directly map emotions to harmonic complexity and rhythmic density.
- **Natural Language CLI:** The `make` command understands plain English queries like `"dark travis x metro f# 8 bars"`.
- **Professional MIDI Export:** Exports clean, timeline-synced MIDI stems with proper humanization and swing templates.
- **Producer Style Database:** Built-in profiles for leading artists and producers across trap, drill, R&B, and melodic styles, including expanded entries for Drake, Kendrick Lamar, Playboi Carti, 40, Wheezy, Boi-1da, and Hit-Boy.
- **Professional Generation Template:** Strict API patterns for consistent, error-free beat generation.
- **Error Handling & Logging:** Robust error handling with proper logging for debugging and monitoring.
- **Type Safety:** Full type hints and mypy compatibility for better IDE support and code quality.

## � Recent Updates

Recent work on the generation engine has improved melodic phrasing at phrase boundaries:
- **Boundary-aware collapse:** melody resolution now settles to the nearest active chord tone at cadence points and respects chord changes cleanly.
- **Stronger chord anchoring:** dark, high-tension melodies now prefer chord tones more aggressively and avoid repeated stuck-note behavior.
- **Optional humanization:** swing/humanization is now explicitly enabled with `--humanize`, keeping default exports predictable.
- **Expanded style profiles:** the artist/producer database now includes richer, more realistic signatures for modern trap, drill, and R&B-inspired production.
- **Regression coverage:** dedicated crash tests now cover inversion handling, octave jump behavior, and boundary resolution instinct.
- **Repository hygiene:** generated MIDI outputs, caches, and local-only artifacts are now ignored so the repo stays clean for collaborators.

## �📦 Installation

HarmonyForge is built for speed and uses `uv` for ultra-fast dependency management.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install HarmonyForge
git clone https://github.com/Orest-gt/HarmonyForge.git
cd HarmonyForge
uv pip install -e ".[ai]"
```

## 🎹 Usage (CLI)

### Natural Language Mode (Recommended)

Generate stems using plain English:

```bash
uv run harmonyforge make "dark travis x metro f# 8 bars"
uv run harmonyforge make "tay keith x atl jacob d phrygian 163 bpm drill"
uv run harmonyforge make "emotional neo-soul mike dean c dorian 16 bars vocal fills"
```

Add `--humanize` to enable tempo-aware swing and humanization on export.

### Explicit Flags Mode

For precise control over all parameters:

```bash
uv run harmonyforge generate \
  --artist "Future, Travis Scott" \
  --producer "Mike Dean" \
  --prompt "evil luxury ambient" \
  --key "C#" \
  --scale "minor" \
  --bars 64
```

Check the `./output` folder for your MIDI stems!

## 🎛️ Professional Beat Generation

For production-ready beats, use the professional generation template:

```bash
# Copy the template for your beat
cp TEMPLATE_GENERATE_BEAT.py generate_my_beat.py

# Edit the musical parameters section:
# - Choose producer style (NICK_MIRA, METRO_BOOMIN, etc.)
# - Set BPM, key, scale, bars
# - Configure swing style

# Run generation
python generate_my_beat.py
```

**Available Producer Styles:**
- **Nick Mira**: Dark melodic trap, emotional piano, heavy 808s
- **Metro Boomin**: Dark cinematic trap, heavy syncopation
- **Southside**: Aggressive trap, complex rhythms
- **Tay Keith**: Minimal trap, hard-hitting 808s
- **Pierre Bourne**: Melodic trap, synth-heavy
- **Mike Dean**: Emotional neo-soul, rich harmonies
- **Murda Beatz**: Dark trap, intricate patterns
- **ATL Jacob**: Melodic trap, vocal-ready
- **Ronny J**: Experimental trap, distorted elements
- **Frank Dukes**: Professional pop/r&b, polished production

**Output:**
- DAW-ready MIDI stems (stem_chords.mid, stem_melody.mid, stem_bass.mid, stem_counter_melody.mid)
- Proper time signature metadata (4/4)
- Tempo-accurate timing
- Genre-appropriate swing templates (straight, trap_bounce, dilla_swing, drill_push, afro_triplet)

## 🧪 Validation & Benchmarks

HarmonyForge v2.1.0 has been rigorously tested:
- **Code Quality:** Full ruff linting compliance with professional code standards.
- **Type Safety:** Comprehensive type hints for better IDE support and error prevention.
- **Error Handling:** Robust exception handling throughout the codebase.
- **Security:** No unsafe system calls or hardcoded credentials.
- **Timing Accuracy:** MIDI timing verified against Standard MIDI Files specification.
- **API Compliance:** Professional generation template ensures consistent API usage.

To run the test suite:
```bash
uv run pytest tests/
```

To run the parser validation:
```bash
uv run python src/harmonyforge/testing/test_parser.py
```

## 🏗️ Architecture

1. **Phase 1-3:** Music Theory Core (Roman Numerals, Scales, Chords)
2. **Phase 4-5:** Voice Leading & 808 Syncopation (Pitch bend slides)
3. **Phase 6-7:** Hybrid MIDI Export & CLI
4. **Phase 8:** AI Integration (PyTorch Neural Nets & NLP Ontology)
5. **Phase 9:** Arrangement Engine (Macro song structure & Motif Memory)
6. **Phase 10:** Audio Intelligence (Spectral analysis & Mix Feedback)

---
*Created by Devin - Computational Music Specialist.*
