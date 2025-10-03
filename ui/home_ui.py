import streamlit as st
from router import router


def page_home():
    st.title("Bem-vindo à Página Inicial")
    st.write("Selecione uma opção abaixo:")

    if st.button("Listar Usuários"):
        router.route_to('user')

    if st.button("Listar Tipos de Coleta"):
        router.route_to('collect_type')

    if st.button("Listar Pontos de Coleta"):
        router.route_to('collect_point')
