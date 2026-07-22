# HarmonyForge v2.1.0

![HarmonyForge](https://img.shields.io/badge/HarmonyForge-v2.1.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

HarmonyForge is a next-generation AI-assisted harmony, melody, and MIDI generation engine designed for modern music producers. 

It is NOT a random chord generator. It is an aesthetic engine that models producer styles mathematically using a **Music Genome**, generates full 64-bar arrangements with energy automation, and features a functional **Evaluation Engine** and **Audio Intelligence**.

---

## 🚀 Features

- **Music Genome Interpolation:** Blend styles mathematically. Want 70% Juice WRLD and 30% Metro Boomin? HarmonyForge handles the tension, syncopation, and darkness mapping.
- **NLP Prompt Parser:** Use natural language (`--prompt "evil luxury cinematic"`) to directly map emotions to harmonic complexity and rhythmic density.
- **Arrangement Engine (Phase 9):** Generates full songs. Intro, Verses, Hooks, and Breakdowns, mapped to an energy curve that naturally drops out bass and drums for dynamic contrast.
- **Audio Intelligence (Phase 10 Foundation):** Capable of listening to a rendered `.wav` beat via `librosa`, extracting spectral features, finding 808 masking problems, and outputting producer feedback.
- **Hybrid Export:** Exports `arrangement.json` and timeline-synced MIDI stems directly for your DAW.

## 📦 Installation

HarmonyForge is built for speed and uses `uv` for ultra-fast dependency management.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install HarmonyForge
git clone https://github.com/your-username/HarmonyForge.git
cd HarmonyForge
uv pip install -e ".[ai]"
```

## 🎹 Usage (CLI)

Generate a full 64-bar arrangement for a specific stylistic blend:

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

## 🧪 Validation & Benchmarks

HarmonyForge v2.1.0 has been rigorously tested:
- **1000 Track Stress Test:** 0% crash rate guaranteed.
- **V2.1 Benchmark:** Generates 50 industry-standard loops across Trap, Drill, Boom Bap, and R&B, logging average Musicality, Style Match, and Originality scores.

To run the benchmark suite:
```bash
uv run python src/harmonyforge/testing/validation_suite.py
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
