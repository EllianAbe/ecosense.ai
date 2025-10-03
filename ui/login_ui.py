import streamlit as st
from service.auth_service import AuthService
from service.user_service import UserService
from router import router

auth_service = AuthService()
user_service = UserService()


def page_login():
    if 'user' in st.session_state and st.session_state.user:
        router.route_to('home')

    if user_service.is_table_empty():
        router.route_to('first_access')

    st.title("Tela de Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Logar"):
        if user := auth_service.auth(username):
            st.session_state.user = user
            router.route_to('home')
        else:
            st.error("Usuário ou senha incorretos.")
