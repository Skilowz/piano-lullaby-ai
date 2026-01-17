"""
🎹 Piano Lullaby AI — Expressive Edition
Preserves musical feeling, phrasing, pauses and harmonic movement.
"""

import streamlit as st
import librosa
import numpy as np
import yt_dlp
import pretty_midi
import subprocess

# ======================================================
# STREAMLIT CONFIG
# ======================================================

st.set_page_config(
    page_title="Piano Lullaby AI",
    page_icon="🎹",
    layout="wide"
)

st.title("🎹 Piano Lullaby AI")
st.write("Versões de ninar que preservam o feeling, o tempo e a respiração da música original.")

# ======================================================
# YOUTUBE DOWNLOAD
# ======================================================

def download_youtube(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "input",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav"
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "input.wav"

# ======================================================
# MUSICAL ANALYSIS (FEELING AWARE)
# ======================================================

def analyze_music(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")

    rms = librosa.feature.rms(y=y)[0]
    rms_times = librosa.times_like(rms, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    return {
        "y": y,
        "sr": sr,
        "tempo": tempo,
        "duration": duration,
        "beats": beats,
        "rms": rms,
        "rms_times": rms_times,
        "chroma": chroma
    }

# ======================================================
# PHRASE SEGMENTATION (RESPIRAÇÃO MUSICAL)
# ======================================================

def segment_phrases(analysis):
    rms = analysis["rms"]
    times = analysis["rms_times"]

    threshold = np.percentile(rms, 25)
    segments = []

    start = 0
    for i in range(1, len(rms)):
        if rms[i] < threshold and rms[i-1] >= threshold:
            end = times[i]
            if end - start > 0.8:
                segments.append((start, end))
                start = end

    segments.append((start, analysis["duration"]))
    return segments

# ======================================================
# HARMONIC EXTRACTION PER PHRASE
# ======================================================

BABY_CHORDS = [
    [0, 4, 7],   # maior
    [0, 3, 7],   # menor
    [0, 7, 12]   # power / aberto
]

def phrase_to_music(analysis, start, end):
    sr = analysis["sr"]
    chroma = analysis["chroma"]

    t_start = int(start * sr / 512)
    t_end = int(end * sr / 512)

    frame = chroma[:, t_start:t_end].mean(axis=1)
    root = int(np.argmax(frame))

    chord_type = BABY_CHORDS[np.argmax([
        frame[(root + i) % 12] for i in [4, 3, 7]
    ])]

    bass = root - 12
    chord = [(root + i) for i in chord_type]

    energy = analysis["rms"][t_start:t_end].mean()

    return {
        "bass": bass,
        "chord": chord,
        "energy": energy,
        "duration": end - start
    }

# ======================================================
# EXPRESSIVE LULLABY ARRANGEMENT
# ======================================================

def create_lullaby_midi(analysis):
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(
        program=pretty_midi.instrument_name_to_program("Acoustic Grand Piano")
    )

    tempo = max(55, min(70, analysis["tempo"] * 0.65))
    seconds_per_beat = 60 / tempo

    phrases = segment_phrases(analysis)

    time = 0.0

    for start, end in phrases:
        phrase = phrase_to_music(analysis, start, end)

        if phrase["energy"] < np.percentile(analysis["rms"], 20):
            time += phrase["duration"] * 0.8
            continue

        # baixo
        piano.notes.append(
            pretty_midi.Note(
                velocity=35,
                pitch=48 + phrase["bass"] % 12,
                start=time,
                end=time + seconds_per_beat * 2
            )
        )

        # arpejo
        arp_time = time
        for n in phrase["chord"]:
            piano.notes.append(
                pretty_midi.Note(
                    velocity=40,
                    pitch=60 + n,
                    start=arp_time,
                    end=arp_time + seconds_per_beat
                )
            )
            arp_time += seconds_per_beat * 0.75

        time += phrase["duration"]

    midi.instruments.append(piano)
    midi.write("lullaby.mid")

# ======================================================
# REAL PIANO RENDERING
# ======================================================

def render_piano():
    subprocess.run([
        "fluidsynth",
        "-ni",
        "piano_felt.sf2",
        "lullaby.mid",
        "-F",
        "output.wav",
        "-r",
        "22050"
    ], check=True)

# ======================================================
# STREAMLIT UI
# ======================================================

uploaded = st.file_uploader("Upload MP3 ou WAV", type=["mp3", "wav"])
yt_url = st.text_input("Ou cole um link do YouTube")

if st.button("🎼 GERAR LULLABY EXPRESSIVA"):
    try:
        with st.spinner("Analisando feeling musical e criando arranjo expressivo..."):
            if yt_url:
                input_path = download_youtube(yt_url)
            else:
                input_path = "input.wav"
                with open(input_path, "wb") as f:
                    f.write(uploaded.getbuffer())

            analysis = analyze_music(input_path)
            create_lullaby_midi(analysis)
            render_piano()

            st.audio("output.wav")
            st.success("Versão de ninar criada com feeling preservado 🎹🍼")

    except Exception as e:
        st.error(f"Erro: {e}")
