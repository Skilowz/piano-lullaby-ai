import streamlit as st
import librosa
import yt_dlp
import os

from perception.perception_engine import perceive
from memory.chord_memory import detect_chords
from translation.harmony_reducer import reduce_harmony
from performance.midi_builder import build_midi
from performance.render import render

# --------------------------------------------------
# STREAMLIT CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Lullaby Studio",
    page_icon="🎹",
    layout="wide"
)

st.title("🎹 AI Lullaby Studio")
st.write("Transforme qualquer música em uma versão de ninar emocional e musicalmente fiel.")

# --------------------------------------------------
# INPUT
# --------------------------------------------------

uploaded = st.file_uploader("Upload MP3 ou WAV", type=["mp3", "wav"])
yt_url = st.text_input("Ou link do YouTube")

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

# --------------------------------------------------
# PROCESS
# --------------------------------------------------

if st.button("🎼 GERAR LULLABY"):
    try:
        with st.spinner("Entendendo a música como um humano..."):
            if yt_url:
                input_path = download_youtube(yt_url)
            else:
                input_path = "input.wav"
                with open(input_path, "wb") as f:
                    f.write(uploaded.read())

            perception = perceive(input_path)

        with st.spinner("Extraindo memória musical..."):
            y, sr = librosa.load(input_path, sr=22050)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chords_raw = detect_chords(chroma)

        with st.spinner("Traduzindo para linguagem de bebê..."):
            chords_lullaby = [reduce_harmony(c) for c in chords_raw]

        with st.spinner("Tocando como um humano..."):
            timeline = list(zip(
                perception["beats"][:-1],
                perception["beats"][1:]
            ))

            build_midi(
                chords_lullaby,
                timeline,
                perception["emotion"]
            )

            render()

        st.audio("output.wav")
        st.success("Lullaby criada com feeling e duração preservados 🎹🍼")

    except Exception as e:
        st.error(f"Erro: {e}")
