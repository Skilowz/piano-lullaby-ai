import librosa
import numpy as np

from perception.audio_loader import load_audio
from perception.phrase_detection import detect_phrases
from perception.vocal_analysis import analyze_vocals
from perception.emotion_curve import extract_emotion_curve


def perceive(audio_path):
    """
    Percepção musical global:
    - tempo
    - duração
    - frases
    - vocal
    - curva emocional
    """

    # ========= LOAD =========
    y, sr = load_audio(audio_path)

    duration = librosa.get_duration(y=y, sr=sr)

    # ========= TEMPO =========
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # ========= FRASES =========
    phrases = detect_phrases(y, sr)

    # ========= VOCAL =========
    vocal_features = analyze_vocals(y, sr)

    # ========= EMOÇÃO =========
    emotion = extract_emotion_curve(y, sr)

    return {
        "audio": y,
        "sr": sr,
        "duration": duration,
        "tempo": float(tempo),
        "phrases": phrases,
        "vocal": vocal_features,
        "emotion": emotion
    }
