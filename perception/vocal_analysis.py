import librosa
import numpy as np

def analyze_vocals(y, sr):
    pitches, mags = librosa.piptrack(y=y, sr=sr)
    pitch_track = pitches[mags > np.median(mags)]
    return {
        "mean_pitch": float(np.mean(pitch_track)) if len(pitch_track) else 0.0,
        "expressiveness": float(np.std(pitch_track)) if len(pitch_track) else 0.0
    }
