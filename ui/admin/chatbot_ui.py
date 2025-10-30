import streamlit as st
from service.chatbot_service import ChatbotService
from navigation import navigation

def page_chatbot():
    st.header("🤖 Chatbot de IA")

    chatbot_service = ChatbotService()

    # Chat section
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

    user_input = st.chat_input("Digite sua mensagem...")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        ai_response = chatbot_service.get_response(user_input)
        st.session_state.chat_history.append(("assistant", ai_response))
        st.rerun()

    st.divider()

    # Image analysis section
    st.subheader("📸 Envie uma imagem para análise")
    uploaded_file = st.file_uploader("Selecione uma imagem", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagem enviada", width="stretch")

        if st.button("Analisar imagem"):
            with st.spinner("Analisando imagem..."):
                result = chatbot_service.analyze_image(uploaded_file)
                st.success("Resultado:")
                st.write(result)
