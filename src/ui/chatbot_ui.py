import streamlit as st
from service.chatbot_service import ChatbotService
from utils.navigation import navigation
from streamlit_geolocation import streamlit_geolocation

chatbot_service = ChatbotService()


def page_chatbot():

    st.subheader("📸 Envie uma imagem para análise")

    with st.container(horizontal=True, vertical_alignment="center"):
        with st.container(width=34):
            location = streamlit_geolocation()

        if location['latitude'] and location['longitude']:
            st.session_state['user_location'] = (
                (location['latitude'],
                 location['longitude'])
            )
            st.markdown(
                'localização capturada com sucesso ! :round_pushpin:')
        else:
            st.markdown(
                '⬅️ clique aqui para capturar sua localização !')

    uploaded_file = None
    with st.container(horizontal=True):

        uploaded_file = st.file_uploader(
            "Selecione uma imagem",
            type=["jpg", "jpeg", "png"],
            label_visibility='collapsed',
            width=400)

        if uploaded_file:
            st.image(
                uploaded_file,
                caption="Imagem enviada",
                width=200)

    if st.button("Analisar Imagem", disabled=not uploaded_file):
        with st.spinner("Analisando imagem..."):
            points_result = chatbot_service.search_collect_points(
                uploaded_file, st.session_state.get('user_location'))
            materials_result = chatbot_service.describe_materials(
                points_result['description'])

            render_analysis_results(
                points_result,
                materials_result,
                uploaded_file
            )


def render_collect_point_card(col, collect_point, collect_types, geographic_distance=None, **kwargs):
    if geographic_distance:
        distance_text = f"{geographic_distance:.2f} km"
    else:
        distance_text = "N/A"

    col.markdown(
        f"""
        **{collect_point.description}**  
        {collect_point.street}, {collect_point.number}, {collect_point.cep}  
        {collect_point.city} - {collect_point.state}  
        {collect_point.contact_name}  
        {collect_point.phone} - {collect_point.email}
        📍 **{distance_text}**
        """
    )

    col.markdown(
        '<small>' +
        ' '.join(['`' + t.description + '`' for t in collect_types]) +
        '</small>',
        unsafe_allow_html=True
    )


@st.dialog('Análise de Imagem', width='large')
def render_analysis_results(points_result, materials_result, uploaded_image):
    """
    Exibe todos os resultados da análise em abas organizadas.

    Args:
        points_result: dict com 'description' e 'collect_points'
        materials_result: str com descrição dos materiais
    """

    # Criar abas para cada resultado
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Pontos de Coleta",
        "🔍 Materiais",
        "🌍 Impacto Ambiental",
        "⚕️ Impacto na Saúde",
        "🤖 Chatbot",
    ])

    # Aba 1: Pontos de Coleta
    with tab1:
        collect_points = points_result.get('collect_points', [])

        if not collect_points:
            st.warning("Nenhum ponto de coleta encontrado para esta imagem.")
        else:
            st.subheader(f"Encontrados {len(collect_points)} pontos de coleta")

            for i in range(0, len(collect_points), 3):
                row = st.container(horizontal=True)

                next_group = collect_points[i: i + 3]

                for i, collect_point in enumerate(next_group):
                    col = row.columns(1, border=True)[0]
                    render_collect_point_card(col=col, **collect_point)

                for j in range(i, 2):
                    row.columns(1)

    # Aba 2: Descrição de Materiais
    with tab2:
        st.subheader("Identificação de Materiais")
        if materials_result:
            st.info(materials_result)
        else:
            st.warning("Nenhum resultado de análise de materiais disponível.")

    # Aba 3: Impacto Ambiental
    with tab3:
        st.subheader("Análise de Impacto Ambiental")

        if st.button('Pesquisar Impactos Ambientais'):
            with st.spinner('Pesquisando impactos ambientais'):
                environment_result = chatbot_service.describe_environment_impact(
                    points_result['description'], materials_result)

            if environment_result:
                st.success(environment_result)
            else:
                st.warning("Nenhum resultado de impacto ambiental disponível.")

    # Aba 4: Impacto na Saúde
    with tab4:
        st.subheader("Análise de Impacto na Saúde")

        if st.button('Pesquisar Impactos na Saúde'):
            with st.spinner('Pesquisando impactos na saúde humana'):
                health_result = chatbot_service.describe_health_impact(
                    points_result['description'], materials_result)

            if health_result:
                st.warning(health_result)
            else:
                st.warning("Nenhum resultado de impacto na saúde disponível.")

    # Aba 5: Chatbot
    with tab5:
        st.subheader("Chatbot")
        st.image(uploaded_image, caption="Imagem enviada", width=200)
        user_query = st.chat_input(
            placeholder="Faça uma pergunta sobre a imagem",
            key="chatbot_input"
        )

        if user_query:
            user_message = st.session_state["chatbot_input"]
            st.chat_message("user").markdown(user_message)

            with st.spinner("Processando resposta do chatbot..."):
                bot_response = chatbot_service.chatbot(
                    uploaded_image,
                    user_message
                )

            st.chat_message("assistant").markdown(bot_response)
