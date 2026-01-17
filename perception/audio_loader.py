import librosa

def load_audio(path):
    return librosa.load(path, sr=22050, mono=True)
