"""
🎹 Piano Lullaby AI
Recomposes any song into a professional acoustic piano lullaby for babies.
"""

import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import yt_dlp
import pretty_midi
import subprocess
import os

# ======================================================
# STREAMLIT CONFIG
# ======================================================

st.set_page_config(
    page_title="Piano Lullaby AI",
    page_icon="🎹",
    layout="wide"
)

st.title("🎹 Piano Lullaby AI")
st.write("Transforme qualquer música em uma versão profissional de piano para ninar bebês.")

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
# MUSICAL ANALYSIS (IA MUSICAL)
# ======================================================

def analyze_music(path):
    y, sr = librosa.load(path, sr=22050, mono=True)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    energy = chroma.mean(axis=1)

    key_index = int(np.argmax(energy))
    key_note = librosa.midi_to_note(60 + key_index)

    return {
        "tempo": tempo,
        "key": key_note,
        "chroma": chroma
    }

# ======================================================
# BABY-SAFE HARMONIC REDUCTION
# ======================================================

BABY_INTERVALS = [0, 4, 7]  # uníssono, terça maior, quinta justa

def reduce_harmony(chroma):
    notes = []
    step = 12  # resolução lenta (previsível)

    for t in range(0, chroma.shape[1], step):
        frame = chroma[:, t]
        root = int(np.argmax(frame))

        for interval in BABY_INTERVALS:
            notes.append((root + interval) % 12)

    return notes

# ======================================================
# GENERATIVE LULLABY ARRANGEMENT
# ======================================================

def create_lullaby_midi(notes, base_tempo):
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("Acoustic Grand Piano"))

    tempo = max(55, min(70, base_tempo * 0.65))
    beat = 60 / tempo

    time = 0.0
    for n in notes:
        pitch = 60 + n  # região central do piano
        note = pretty_midi.Note(
            velocity=42,
            pitch=pitch,
            start=time,
            end=time + beat * 2
        )
        piano.notes.append(note)
        time += beat * 2

    midi.instruments.append(piano)
    midi.write("lullaby.mid")

# ======================================================
# REAL PIANO RENDERING (FLUIDSYNTH)
# ======================================================

def render_piano():
    command = [
        "fluidsynth",
        "-ni",
        "piano_felt.sf2",
        "lullaby.mid",
        "-F",
        "output.wav",
        "-r",
        "22050"
    ]
    subprocess.run(command, check=True)

# ======================================================
# STREAMLIT UI
# ======================================================

uploaded = st.file_uploader("Upload MP3 ou WAV", type=["mp3", "wav"])
yt_url = st.text_input("Ou cole um link do YouTube")

if st.button("🎼 GERAR LULLABY"):
    try:
        with st.spinner("Analisando música e criando arranjo de ninar..."):
            if yt_url:
                input_path = download_youtube(yt_url)
            else:
                input_path = "input.wav"
                with open(input_path, "wb") as f:
                    f.write(uploaded.getbuffer())

            analysis = analyze_music(input_path)
            notes = reduce_harmony(analysis["chroma"])
            create_lullaby_midi(notes, analysis["tempo"])
            render_piano()

            st.audio("output.wav")
            st.success("Versão de ninar criada com sucesso 🎹🍼")

    except Exception as e:
        st.error(f"Erro: {e}")
