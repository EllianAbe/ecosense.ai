import streamlit as st
from navigation import navigation


def go_back_button():
    previous = st.session_state.get('previous_page')
    if st.button('Voltar', disabled=not previous):
        navigation.goto(previous)
