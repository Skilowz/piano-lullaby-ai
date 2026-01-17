"""
🎹 Piano Lullaby AI
Recomposes any song into a professional acoustic piano lullaby
with the SAME duration as the original music.
"""

import streamlit as st
import librosa
import numpy as np
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
st.write("Transforme qualquer música em uma versão de piano para ninar bebês, mantendo a duração original.")

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

    duration = librosa.get_duration(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    energy = chroma.mean(axis=1)

    key_index = int(np.argmax(energy))
    key_note = librosa.midi_to_note(60 + key_index)

    return {
        "tempo": tempo,
        "duration": duration,
        "chroma": chroma,
        "key": key_note
    }

# ======================================================
# BABY-SAFE HARMONIC REDUCTION
# ======================================================

BABY_INTERVALS = [0, 4, 7]  # consonantes

def reduce_harmony(chroma, total_notes):
    notes = []
    step = max(1, chroma.shape[1] // total_notes)

    for t in range(0, chroma.shape[1], step):
        frame = chroma[:, t]
        root = int(np.argmax(frame))
        notes.append(root)

        if len(notes) >= total_notes:
            break

    return notes

# ======================================================
# GENERATIVE LULLABY ARRANGEMENT
# ======================================================

def create_lullaby_midi(notes, base_tempo, total_duration):
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(
        program=pretty_midi.instrument_name_to_program("Acoustic Grand Piano")
    )

    tempo = max(55, min(70, base_tempo * 0.65))
    seconds_per_beat = 60 / tempo
    note_duration = seconds_per_beat * 2  # notas longas e calmas

    total_notes = int(total_duration / note_duration)
    notes = notes[:total_notes]

    time = 0.0
    for n in notes:
        pitch = 60 + n
        note = pretty_midi.Note(
            velocity=40,
            pitch=pitch,
            start=time,
            end=time + note_duration
        )
        piano.notes.append(note)
        time += note_duration

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
        with st.spinner("Analisando música e criando versão de ninar..."):
            if yt_url:
                input_path = download_youtube(yt_url)
            else:
                input_path = "input.wav"
                with open(input_path, "wb") as f:
                    f.write(uploaded.getbuffer())

            analysis = analyze_music(input_path)

            tempo_lullaby = max(55, min(70, analysis["tempo"] * 0.65))
            note_duration = (60 / tempo_lullaby) * 2
            total_notes = int(analysis["duration"] / note_duration)

            notes = reduce_harmony(analysis["chroma"], total_notes)

            create_lullaby_midi(
                notes,
                analysis["tempo"],
                analysis["duration"]
            )

            render_piano()

            st.audio("output.wav")
            st.success("Versão de ninar criada mantendo a duração original 🎹🍼")

    except Exception as e:
        st.error(f"Erro: {e}")
