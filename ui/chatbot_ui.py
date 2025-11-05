import streamlit as st
from service.chatbot_service import ChatbotService
from navigation import navigation


def page_chatbot():
    chatbot_service = ChatbotService()

    # Chat section
    # if "chat_history" not in st.session_state:
    #     st.session_state.chat_history = []

    # for role, message in st.session_state.chat_history:
    #     with st.chat_message(role):
    #         st.markdown(message)

    # user_input = st.chat_input("Digite sua mensagem...")
    # if user_input:
    #     st.session_state.chat_history.append(("user", user_input))
    #     ai_response = chatbot_service.get_response(user_input)
    #     st.session_state.chat_history.append(("assistant", ai_response))
    #     st.rerun()

    # Image analysis section
    st.subheader("📸 Envie uma imagem para análise")

    uploaded_file = st.file_uploader(
        "Selecione uma imagem", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        col, _ = st.columns([2, 3])
        col.image(uploaded_file, caption="Imagem enviada", width="stretch")

        if st.button("Analisar imagem"):
            with st.spinner("Analisando imagem..."):
                result = chatbot_service.search_collect_points(uploaded_file)

            with st.expander('Ver Descrição'):
                st.write(result['description'])
            
            # Add: Checagem de "INVÁLIDO"
            if result['description'].strip().upper() == "INVÁLIDO":
                st.error("Imagem inválida - por favor avalie a imagem e envie novamente")
                return

            collect_points = result['collect_points']

            if not collect_points:
                st.warning(
                    "Nenhum ponto de coleta encontrado para esta imagem.")
                return
            collect_points = list(collect_points.values())

            for i in range(0, len(collect_points), 2):
                row = st.container(horizontal=True)

                next_group = collect_points[i: i + 2]

                for i, collect_point in enumerate(next_group):
                    point = collect_point['collect_point']
                    types = collect_point['collect_types']

                    col = row.columns(1, border=True)[0]
                    col.markdown(
                        f"""
                        **{point.description}**  
                        {point.street}, {point.number}, {point.cep}  
                        {point.city} - {point.state}  
                        {point.contact_name}  
                        {point.phone} - {point.email}
                        """
                    )

                    col.markdown(
                        '<small>' +
                        ' '.join(
                            ['`' + type.description + '`' for type in types]) +
                        '</small>',
                        unsafe_allow_html=True
                    )

                for j in range(i, 1):
                    row.columns(1)
