"""
Phase 10: Audio Intelligence.
Analyzes rendered audio files (.wav) to extract musical and spectral features,
providing actionable mix and arrangement feedback.
"""

from typing import List, Dict, Any
from pydantic import BaseModel
import numpy as np

try:
    import librosa
except ImportError:
    pass

class AudioReport(BaseModel):
    """Schema for the Audio Intelligence Report."""
    # Musical Features
    key: str
    bpm: float
    mood_prediction: str
    
    # Arrangement Features
    energy_curve: List[float] # RMS energy over time blocks
    section_analysis: List[Dict[str, Any]] # Bounds and properties of sections
    arrangement_score: float # 0.0 to 1.0 rating of macro-dynamics
    
    # Spectral & Mix Features
    spectral_profile: Dict[str, float] # e.g. centroid, rolloff, bandwidth
    frequency_bands: Dict[str, float] # Energy in sub, bass, mid, high
    
    # Producer Feedback
    mix_issues: List[str]
    suggestions: List[str]
    
    # Reverse Mapped Genome (Future Architecture)
    predicted_genome_shifts: Dict[str, float]


def extract_features(audio_path: str) -> AudioReport:
    """
    Loads an audio file and performs deep functional extraction using librosa and scipy.
    """
    # 1. Load Audio
    y, sr = librosa.load(audio_path, sr=None)
    
    # 2. Extract Tempo and Key
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    bpm = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
    
    # Simple chroma for key detection
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_idx = np.argmax(np.sum(chroma, axis=1))
    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    detected_key = pitch_classes[key_idx]
    
    # 3. Energy Curve (RMS)
    rms = librosa.feature.rms(y=y)[0]
    # Downsample RMS into 10 manageable blocks for the curve
    energy_blocks = np.array_split(rms, min(10, len(rms)))
    energy_curve = [float(np.mean(block)) for block in energy_blocks]
    
    # Normalize energy curve to 0.0 - 1.0
    max_e = max(energy_curve) if max(energy_curve) > 0 else 1.0
    energy_curve = [e / max_e for e in energy_curve]
    
    # 4. Spectral Profile
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    spectral_profile = {
        "mean_centroid_hz": float(np.mean(centroid)),
        "mean_rolloff_hz": float(np.mean(rolloff))
    }
    
    # 5. Frequency Band Analysis (Sub, Bass, Mid, High)
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    
    # Indices for bands
    sub_idx = np.where(freqs < 60)[0]
    bass_idx = np.where((freqs >= 60) & (freqs < 250))[0]
    mid_idx = np.where((freqs >= 250) & (freqs < 2000))[0]
    high_idx = np.where(freqs >= 2000)[0]
    
    bands = {
        "sub": float(np.mean(S[sub_idx, :])) if len(sub_idx) else 0.0,
        "bass": float(np.mean(S[bass_idx, :])) if len(bass_idx) else 0.0,
        "mid": float(np.mean(S[mid_idx, :])) if len(mid_idx) else 0.0,
        "high": float(np.mean(S[high_idx, :])) if len(high_idx) else 0.0,
    }
    
    # 6. Analyze Mix Issues and Suggestions
    issues = []
    suggestions = []
    
    if bands["sub"] > bands["bass"] * 2:
        issues.append("808/Sub energy is overwhelmingly dominating the bass region (potential masking).")
        suggestions.append("Apply a high-pass filter or turn down the 808 slightly.")
        
    if spectral_profile["mean_centroid_hz"] < 500:
        issues.append("Track sounds muddy (Spectral Centroid is unusually low).")
        suggestions.append("Remove pad in verse or high-pass mid-range synths.")
        
    dynamic_range = max(energy_curve) - min(energy_curve)
    arrangement_score = max(0.0, min(1.0, dynamic_range * 1.5))
    
    if arrangement_score < 0.4:
        issues.append("Low contrast between sections. The song lacks dynamic arrangement.")
        suggestions.append("Increase drum density by 20% in the hook and drop elements in the verse.")
        
    # 7. Audio -> Music Genome Reverse Mapping Foundation
    # If the track is highly energetic and syncopated, we map it back to genome parameters
    predicted_genome_shifts = {
        "rhythmic_density": float(bpm / 200.0), # Simplistic mapping
        "darkness_level": 0.8 if "minor" in detected_key.lower() else 0.2, # We don't have minor/major detection yet
        "tension_preference": float(arrangement_score)
    }

    return AudioReport(
        key=detected_key,
        bpm=bpm,
        mood_prediction="Dark/Aggressive" if spectral_profile["mean_centroid_hz"] < 800 else "Bright",
        energy_curve=energy_curve,
        section_analysis=[], # Placeholder for advanced segment boundary detection
        arrangement_score=arrangement_score,
        spectral_profile=spectral_profile,
        frequency_bands=bands,
        mix_issues=issues,
        suggestions=suggestions,
        predicted_genome_shifts=predicted_genome_shifts
    )
