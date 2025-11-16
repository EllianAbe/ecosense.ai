import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from utils.navigation import navigation


def card(title, desc, key, icon="♻️", target=None):
    with st.container(width=200, border=True):
        st.markdown(f"### {icon} {title}")
        st.write(desc)

        if st.button('ir', key=key, width='stretch'):
            navigation.goto(target)
