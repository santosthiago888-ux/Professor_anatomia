import json
import re
from pathlib import Path
import streamlit as st
from crewai import Agent, Task, Crew, Process

st.set_page_config(page_title="Professor de Anatomia Veterinária", page_icon="🦴", layout="centered")

def ler_jsonc(caminho: Path) -> dict:
    """Lê um arquivo .jsonc removendo comentários // e /* */."""
    texto = caminho.read_text(encoding="utf-8")
    texto = re.sub(r"//.*", "", texto)
    texto = re.sub(r"/\*[\s\S]*?\*/", "", texto)
    return json.loads(texto)

def montar_crew(pergunta: str) -> Crew:
    """Carrega crew.jsonc e os agentes da pasta agents/."""
    base_dir = Path(__file__).parent
    crew_cfg = ler_jsonc(base_dir / "crew.jsonc")

    agentes = {}
    for nome_agente in crew_cfg["agents"]:
        arq_jsonc = base_dir / "agents" / f"{nome_agente}.jsonc"
        arq_json = base_dir / "agents" / f"{nome_agente}.json"
        ag_cfg = ler_jsonc(arq_jsonc if arq_jsonc.exists() else arq_json)

        settings = ag_cfg.get("settings", {})
        agentes[nome_agente] = Agent(
            role=ag_cfg["role"].format(pergunta=pergunta),
            goal=ag_cfg["goal"].format(pergunta=pergunta),
            backstory=ag_cfg["backstory"].format(pergunta=pergunta),
            llm=ag_cfg.get("llm"),
            verbose=settings.get("verbose", False),
            allow_delegation=settings.get("allow_delegation", False),
        )

    tarefas_por_nome = {}
    lista_tarefas = []
    for t_cfg in crew_cfg["tasks"]:
        contexto = [tarefas_por_nome[c] for c in t_cfg.get("context", []) if c in tarefas_por_nome]
        tarefa = Task(
            description=t_cfg["description"].format(pergunta=pergunta),
            expected_output=t_cfg["expected_output"].format(pergunta=pergunta),
            agent=agentes[t_cfg["agent"]],
            context=contexto or None,
            markdown=t_cfg.get("markdown", False),
        )
        if "name" in t_cfg:
            tarefas_por_nome[t_cfg["name"]] = tarefa
        lista_tarefas.append(tarefa)

    return Crew(
        agents=list(agentes.values()),
        tasks=lista_tarefas,
        process=Process.sequential,
        verbose=crew_cfg.get("verbose", False),
    )

st.title("🦴 Professor de Anatomia Animal")
st.markdown("Faça sua pergunta sobre anatomia veterinária comparada e receba um guia de estudo completo baseado na **NAV**.")

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
                crew = montar_crew(pergunta)
                resultado = crew.kickoff()

                st.success("Material pronto!")
                st.markdown("---")
                st.markdown(resultado.raw)

                st.download_button(
                    label="📥 Baixar Guia de Estudo (.md)",
                    data=resultado.raw,
                    file_name="guia_anatomia.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução: {e}")
