import librosa
import numpy as np

def extract_emotion_curve(y, sr):
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    energy = librosa.feature.rms(y=y)[0]
    return {
        "energy_mean": float(np.mean(energy)),
        "energy_curve": energy.tolist()
    }
