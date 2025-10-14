import streamlit as st
from service.auth_service import AuthService
from service.user_service import UserService
from navigation import navigation
auth_service = AuthService()
user_service = UserService()


def page_login():
    if 'user' in st.session_state and st.session_state.user:
        navigation.goto('home')

    if user_service.is_table_empty():
        navigation.goto('first_access')

    st.title("Tela de Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Logar"):
        if user := auth_service.auth(username):
            st.session_state.user = user
            navigation.goto('home')
        else:
            st.error("Usuário ou senha incorretos.")


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()
