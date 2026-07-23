# Changelog

All notable changes to HarmonyForge will be documented in this file.

## [Unreleased] - 2026-07-23

### Fixed
- **Harmonic Gravity Collapse:** Boundary resolution now collapses to the nearest active chord tone and handles chord changes more musically at phrase cadences.
- **Regression Tests:** Added crash-style regression coverage for inversion handling, octave elasticity, and boundary resolution behavior.

### Improved
- **Repository Hygiene:** Expanded ignore rules to exclude generated MIDI output, local caches, and editor-specific clutter from the shared repository.

## [2.1.0] - 2026-07-23

### Added
- **Professional Generation Template**: `TEMPLATE_GENERATE_BEAT.py` with strict API patterns
- **Producer Style Database**: 10 producer profiles (Nick Mira, Metro Boomin, Southside, Tay Keith, Pierre Bourne, Mike Dean, Murda Beatz, ATL Jacob, Ronny J, Frank Dukes)
- **OREST_PRODUCTIONS**: Sample Nick Mira beat demonstrating professional output
- **TimeSignature Metadata**: Proper 4/4 time signature at time=0.0 for DAW compatibility
- **Nick Mira Producer Profile**: Dark melodic trap style signature

### Fixed
- **Timing Standards**: Corrected TimeSignature parameter from tick 0 to time 0.0 (seconds) per MIDI documentation
- **Version Consistency**: Standardized all version strings to v2.1.0 across project files
- **API Compliance**: Fixed function signature usage in generation scripts
- **Git Configuration**: Updated .gitignore to allow production MIDI files

### Improved
- **Error Handling**: Robust exception handling throughout codebase
- **Type Safety**: Comprehensive type hints and mypy compatibility
- **Code Quality**: Full ruff linting compliance
- **Security**: Replaced unsafe os.system() with subprocess.run()
- **Documentation**: Updated README with generation template usage
- **Logging**: Professional logging configuration for debugging

### Technical Details
- MIDI timing now follows Standard MIDI Files specification
- Tempo: 120 BPM = 500,000 microseconds per quarter note
- Beat duration: beat_dur = 60.0 / bpm (seconds per beat)
- 16th note duration: grid_16th_dur = beat_dur / 4.0
- All generation functions use correct parameter patterns
- Producer profiles accessed via .signature attribute

## [2.0.0] - Initial Release

### Features
- Music Genome Interpolation system
- NLP Prompt Parser
- Natural Language CLI
- Professional MIDI Export
- Voice Leading & 808 Syncopation
- Swing Templates (straight, trap_bounce, dilla_swing, drill_push, afro_triplet)
- Humanization Engine