import os
import streamlit as st
from crewai.project import CrewBase # ou carregamento direto via CrewAI

# Nota: No CrewAI v1.15+, você pode carregar o projeto JSONC diretamente:
from crewai.cli.create_crew import load_crew_from_jsonc

st.set_page_config(page_title="Professor de Anatomia Veterinária", page_icon="🦴", layout="centered")

st.title("🦴 Professor de Anatomia Animal")
st.markdown("Faça sua pergunta sobre anatomia veterinária comparada e receba um guia de estudo completo baseado na **NAV**.")

# Campo de entrada para o usuário
pergunta = st.text_area(
    "Qual estrutura, sistema ou tema você deseja estudar?",
    placeholder="Ex: Diferenças anatômicas do estômago entre equinos, ruminantes e carnívoros",
    height=100
)

if st.button("Gerar Guia de Estudo", type="primary"):
    if not pergunta.strip():
        st.warning("Por favor, digite uma pergunta antes de continuar.")
    else:
        with st.spinner("O Professor de Anatomia e o Redator estão preparando o material..."):
            try:
                crew = load_crew_from_jsonc("crew.jsonc")
                resultado = crew.kickoff(inputs={"pergunta": pergunta})
                
                st.success("Material pronto!")
                st.markdown("---")
                st.markdown(resultado.raw)
            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução: {e}")
