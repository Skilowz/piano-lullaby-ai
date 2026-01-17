import os
import sys
import streamlit as st
import soundfile as sf
import yt_dlp
from pydub import AudioSegment

# =========================
# PATH ROOT
# =========================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# =========================
# IMPORTS REAIS DO PROJETO
# =========================
from perception.perception_engine import perceive

from memory.chord_memory import build_chord_memory
from memory.motif_extractor import extract_motifs

from translation.harmony_reducer import reduce_harmony
from translation.interval_mapper import map_intervals
from translation.lullaby_rules import apply_lullaby_rules

from performance.render import render_audio

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(
    page_title="🎹 Piano Lullaby AI",
    page_icon="🎼",
    layout="wide"
)

st.title("🎹 Piano Lullaby AI")
st.write(
    "Conversão musical avançada: preserva **tempo, feeling, pausas e fraseado**, "
    "traduzindo para piano acústico de ninar."
)

# =========================
# INPUTS
# =========================
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📂 Upload MP3 ou WAV",
        type=["mp3", "wav"]
    )

with col2:
    youtube_url = st.text_input("🔗 Link do YouTube")

generate = st.button("🎼 Gerar versão de ninar")

# =========================
# PIPELINE
# =========================
if generate:
    try:
        with st.spinner("🎧 Processando música..."):
            os.makedirs("assets/uploads", exist_ok=True)
            os.makedirs("assets/outputs", exist_ok=True)

            input_path = "assets/uploads/input.wav"

            # -------- YOUTUBE --------
            if youtube_url:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": "assets/uploads/temp",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "wav"
                    }],
                    "quiet": True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                input_path = "assets/uploads/temp.wav"

            # -------- UPLOAD --------
            elif uploaded_file:
                audio = AudioSegment.from_file(uploaded_file)
                audio.export(input_path, format="wav")
            else:
                st.warning("Envie um arquivo ou link.")
                st.stop()

            # =========================
            # 1️⃣ PERCEPÇÃO
            # =========================
            perception = perceive(input_path)

            # =========================
            # 2️⃣ MEMÓRIA MUSICAL
            # =========================
            chords = build_chord_memory(perception)
            motifs = extract_motifs(perception)

            # =========================
            # 3️⃣ TRADUÇÃO PARA NINAR
            # =========================
            reduced = reduce_harmony(chords)
            mapped = map_intervals(reduced)
            lullaby_score = apply_lullaby_rules(
                mapped,
                motifs,
                tempo=perception["tempo"]
            )

            # =========================
            # 4️⃣ RENDER
            # =========================
            audio_out, sr = render_audio(
                lullaby_score,
                duration=perception["duration"],
                soundfont="assets/piano_felt.sf2"
            )

            output_path = "assets/outputs/piano_lullaby.wav"
            sf.write(output_path, audio_out, sr)

        # =========================
        # OUTPUT
        # =========================
        st.success("✨ Música gerada com sucesso")
        st.audio(output_path)

        st.caption(
            f"Duração: {int(perception['duration'])}s | "
            f"Tempo: {int(perception['tempo'])} BPM"
        )

    except Exception as e:
        st.error("Erro no processamento")
        st.exception(e)
