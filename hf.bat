@echo off
REM HarmonyForge launcher — run from project root or add to PATH.
REM Usage: hf make "dark travis x metro f# 8 bars"
REM        hf generate --artist "Travis Scott" --producer "Metro Boomin" --key F# --scale harmonic_minor
python -m harmonyforge.cli.main %*
