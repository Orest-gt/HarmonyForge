# Contributing to HarmonyForge

Thank you for your interest in contributing to HarmonyForge!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Orest-gt/HarmonyForge.git
   cd HarmonyForge
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e ".[ai,dev]"
   ```

3. **Run tests:**
   ```bash
   uv run pytest tests/
   ```

4. **Run linting:**
   ```bash
   uv run ruff check .
   uv run mypy src/
   ```

## Code Standards

### API Usage
- **Always use `TEMPLATE_GENERATE_BEAT.py`** as a reference for generation scripts
- Use `.signature` attribute when accessing producer profiles
- Follow exact function signatures as defined in the template
- Test generation scripts before committing

### Code Quality
- Follow ruff linting standards
- Add type hints to all functions
- Use proper error handling with try-except blocks
- Add docstrings to new functions and classes

### MIDI Standards
- Use `time=0.0` (seconds) for TimeSignature, not `tick=0`
- Tempo calculations: `beat_dur = 60.0 / bpm`
- Grid calculations: `grid_16th_dur = beat_dur / 4.0`
- Follow Standard MIDI Files specification

## Adding New Producer Profiles

1. Add profile to `src/harmonyforge/styles/producers.py`
2. Follow the StyleSignature structure
3. Test with the generation template
4. Update README with new producer description

## Submission Guidelines

1. Fork the repository
2. Create a feature branch
3. Make your changes following the standards
4. Test thoroughly
5. Submit a pull request

## Questions?

Contact: orestisgatos@gmail.com
