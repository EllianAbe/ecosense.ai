import streamlit as st


def send_feedback(status, message, **ignore):
    if status == 'success':
        st.success(message)
    else:
        st.error(message)
