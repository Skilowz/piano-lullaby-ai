import librosa
import numpy as np

def detect_phrases(y, sr):
    rms = librosa.feature.rms(y=y)[0]
    boundaries = np.where(rms < np.percentile(rms, 20))[0]
    return boundaries.tolist()
