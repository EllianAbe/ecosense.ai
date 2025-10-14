import streamlit as st
from navigation import navigation


def page_home():
    st.title("Bem-vindo à Página Inicial")
    st.write("Selecione uma opção abaixo:")

    if st.button("Listar Usuários"):
        navigation.goto('user')

    if st.button("Listar Tipos de Coleta"):
        navigation.goto('collect_type')

    if st.button("Listar Pontos de Coleta"):
        navigation.goto('collect_point')
