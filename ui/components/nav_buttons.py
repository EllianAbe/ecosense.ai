import streamlit as st
from navigation import navigation


def home_button():
    if st.button('Home'):
        navigation.goto('home')
