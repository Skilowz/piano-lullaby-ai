import streamlit as st
import sys
import os

# =========================
# Garantir path do projeto
# =========================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# =========================
# Imports internos
# =========================
from perception.perception_engine import perceive
from music_memory.chord_memory import build_chord_memory
from translation.lullaby_rules import apply_lullaby_rules
from performance.midi_builder import build_midi
from performance.render import render_audio

# =========================
# Streamlit UI
# =========================
st.set_page_config(
    page_title="Piano Lullaby AI",
    layout="centered"
)

st.title("🎹 Piano Lullaby AI")
st.caption("Transformando emoção em música de ninar")

st.markdown("---")

uploaded_file = st.file_uploader(
    "Envie um áudio (voz, choro, humming, fala)",
    type=["wav", "mp3", "ogg"]
)

generate = st.button("🌙 Gerar Lullaby")

# =========================
# Pipeline Principal
# =========================
if generate and uploaded_file is not None:
    with st.spinner("Analisando emoção e estrutura sonora..."):
        perception = perceive(uploaded_file)

    with st.spinner("Construindo memória harmônica..."):
        harmony_memory = build_chord_memory(perception)

    with st.spinner("Aplicando regras de lullaby..."):
        lullaby_plan = apply_lullaby_rules(harmony_memory)

    with st.spinner("Gerando MIDI..."):
        midi_path = build_midi(lullaby_plan)

    with st.spinner("Renderizando piano..."):
        audio_path = render_audio(
            midi_path=midi_path,
            soundfont_path="assets/piano_felt.sf2"
        )

    st.success("✨ Lullaby criada com sucesso!")

    st.audio(audio_path)

else:
    st.info("Envie um áudio e clique em **Gerar Lullaby** 🎶")
