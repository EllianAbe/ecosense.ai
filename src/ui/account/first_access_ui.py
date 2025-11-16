import streamlit as st
from service.user_service import UserService
from utils.navigation import navigation
user_service = UserService()


def page_first_access():
    st.title("Primeiro Acesso")
    st.write("Bem-vindo! Crie o primeiro usuário administrador.")

    username = st.text_input("Nome de usuário administrador:")
    if st.button("Criar Administrador"):
        if username:
            result = user_service.create_user(username, "admin")
            if result["status"] == "success":
                st.success(result["message"])
                navigation.goto('login')
            else:
                st.error(result["message"])
        else:
            st.warning("Por favor, insira um nome de usuário.")
