import streamlit as st
from router import router


def home_button():
    if st.button('Início'):
        router.route_to('home')
