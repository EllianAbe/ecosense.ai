import streamlit as st
from utils.navigation import navigation
from ui.components.card import card


def page_home():
    st.title("Bem-vindo à EcoSense AI")
    st.write("Escolha uma opção abaixo para navegar pelo sistema:")

    with st.container(horizontal=True, horizontal_alignment='left'):

        card(
            "Usuários",
            "Ver, editar e gerenciar usuários registrados.",
            "btn_users",
            icon="👥",
            target="user",
        )

        card(
            "Tipos de Coleta",
            "Gerencie os tipos de coleta e suas regras.",
            "btn_collect_types",
            icon="🗂️",
            target="collect_type",
        )

        card(
            "Pontos de Coleta",
            "Localize e administre pontos de coleta.",
            "btn_collect_points",
            icon="📍",
            target="collect_point",
        )

        card(
            "Chatbot",
            "Converse com o assistente para orientar usuários.",
            "btn_chatbot",
            icon="🤖",
            target="chatbot",
        )

        card(
            "Metricas",
            "Analise Métricas de qualidade da aplicação.",
            "btn_metrics",
            icon="📈",
            target="metricas",
        )
