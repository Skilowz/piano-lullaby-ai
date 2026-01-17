import os
import sys
import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import yt_dlp
from pydub import AudioSegment

# =========================
# CORREÇÃO CRÍTICA DE PATH
# =========================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# =========================
# IMPORTS DOS MÓDULOS
# =========================
from perception.perception_engine import perceive
from memory.musical_memory import build_harmony
from translation.lullaby_engine import translate_to_lullaby
from performance.render_engine import render_audio

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title="🎹 Piano Lullaby AI",
    page_icon="🎼",
    layout="wide"
)

st.title("🎹 Piano Lullaby AI")
st.write(
    "Transforme qualquer música em uma **versão de piano acústico para ninar**, "
    "preservando o *feeling*, tempo e estrutura musical."
)

# =========================
# UI INPUTS
# =========================
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📂 Upload MP3 ou WAV",
        type=["mp3", "wav"]
    )

with col2:
    youtube_url = st.text_input(
        "🔗 Ou cole um link do YouTube"
    )

generate = st.button("🎼 GERAR VERSÃO DE NINAR")

# =========================
# PROCESSAMENTO
# =========================
if generate:
    try:
        with st.spinner("🎧 Analisando música original..."):
            os.makedirs("assets/uploads", exist_ok=True)
            os.makedirs("assets/outputs", exist_ok=True)

            input_path = "assets/uploads/input.wav"

            # ---------
            # YOUTUBE
            # ---------
            if youtube_url:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "assets/uploads/temp",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "wav",
                        }
                    ],
                    "quiet": True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

                input_path = "assets/uploads/temp.wav"

            # ---------
            # UPLOAD
            # ---------
            elif uploaded_file:
                audio = AudioSegment.from_file(uploaded_file)
                audio.export(input_path, format="wav")

            else:
                st.warning("Envie um arquivo ou link do YouTube.")
                st.stop()

            # =========================
            # 1️⃣ PERCEPÇÃO MUSICAL
            # =========================
            perception_data = perceive(input_path)

            # =========================
            # 2️⃣ MEMÓRIA / HARMONIA
            # =========================
            harmony_data = build_harmony(perception_data)

            # =========================
            # 3️⃣ TRADUÇÃO PARA NINAR
            # =========================
            lullaby_score = translate_to_lullaby(
                harmony_data,
                target_tempo=perception_data["tempo"],  # mantém tempo relativo
                softness=0.85
            )

            # =========================
            # 4️⃣ RENDERIZAÇÃO FINAL
            # =========================
            output_audio, sr = render_audio(
                lullaby_score,
                duration=perception_data["duration"],
                sample_rate=22050
            )

            output_path = "assets/outputs/piano_lullaby.wav"
            sf.write(output_path, output_audio, sr)

        # =========================
        # RESULTADO
        # =========================
        st.success("✨ Música de ninar gerada com sucesso!")
        st.audio(output_path)

        st.caption(
            f"Duração preservada: {int(perception_data['duration'])} segundos | "
            f"Tempo base: {int(perception_data['tempo'])} BPM"
        )

    except Exception as e:
        st.error("❌ Ocorreu um erro durante o processamento.")
        st.exception(e)
