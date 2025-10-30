import streamlit as st
from service.collect_point_service import CollectPointService
from ui.components import feedback
from ui.components import home_button
from navigation import navigation


def page_list_collect_points():
    st.header("Pontos de Coleta Cadastrados")

    collect_point_service = CollectPointService()

    home_button()

    if st.button("Criar Novo Ponto de Coleta"):
        navigation.goto("collect_point/edit")

    collect_points_result = collect_point_service.read_collect_points()

    if collect_points_result['status'] == 'error':
        st.error(collect_points_result['message'])
        return

    collect_points = collect_points_result['data']
    if not collect_points:
        st.info("Nenhum ponto de coleta cadastrado ainda.")
        return

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6, col7 = st.columns(
            [1, 3, 2, 2, 2, 2, 2])

        col1.write("**ID**")
        col2.write("**Descrição**")
        col3.write("**CEP**")
        col4.write("**Cidade**")
        col5.write("**Editar**")
        col6.write("**Deletar**")
        col7.write("**Tipos**")

    for collect_point in collect_points:
        with st.container(border=True):
            col1, col2, col3, col4, col5, col6, col7 = st.columns(
                [1, 3, 2, 2, 2, 2, 2])

            col1.write(collect_point.id)
            col2.write(collect_point.description)
            col3.write(collect_point.cep)
            col4.write(f"{collect_point.city} - {collect_point.state}")

            if col5.button("Editar", key=f"edit_{collect_point.id}"):
                navigation.goto("collect_point/edit",
                                {'collect_point_id': collect_point.id})

            if col6.button("Deletar", key=f"delete_{collect_point.id}"):
                result = collect_point_service.delete_collect_point(
                    collect_point.id)
                feedback.send_feedback(**result)

                st.rerun()

            if col7.button("Tipos", key=f"types_{collect_point.id}"):
                navigation.goto("collect_point/types",
                                {'collect_point_id': collect_point.id})


def page_edit_collect_point():
    collect_point_id = navigation.get_page_args().get('collect_point_id')
    is_edit_mode = collect_point_id is not None
    title = "Editar Ponto de Coleta" if is_edit_mode else "Cadastro de Novo Ponto de Coleta"
    button_label = "Salvar Alterações" if is_edit_mode else "Cadastrar"

    st.header(title)

    collect_point_service = CollectPointService()

    collect_point_to_edit = None
    if is_edit_mode:
        collect_point_result = collect_point_service.get_collect_point(
            collect_point_id)
        if collect_point_result['status'] == 'error':
            st.error(collect_point_result['message'])
            return
        collect_point_to_edit = collect_point_result['data']

    # Campos do formulário
    default_description = collect_point_to_edit.description if collect_point_to_edit else ""
    default_cep = collect_point_to_edit.cep if collect_point_to_edit else ""
    default_street = collect_point_to_edit.street if collect_point_to_edit else ""
    default_number = collect_point_to_edit.number if collect_point_to_edit else ""
    default_city = collect_point_to_edit.city if collect_point_to_edit else ""
    default_state = collect_point_to_edit.state if collect_point_to_edit else ""
    default_contact_name = collect_point_to_edit.contact_name if collect_point_to_edit else ""
    default_phone = collect_point_to_edit.phone if collect_point_to_edit else ""
    default_email = collect_point_to_edit.email if collect_point_to_edit else ""

    with st.form("collect_point_form"):
        description = st.text_input("Descrição", value=default_description)

        cep = st.text_input("CEP", value=default_cep)

        col1, col2 = st.columns([7, 1])
        street = col1.text_input("Rua", value=default_street)

        number = col2.text_input("Número", value=default_number)
        col4, col5, = st.columns([1, 1])
        city = col4.text_input("Cidade", value=default_city)

        state = col5.text_input("Estado", value=default_state)

        contact_name = st.text_input(
            "Nome do Contato", value=default_contact_name)

        col6, col7 = st.columns([1, 3])
        phone = col6.text_input("Telefone", value=default_phone)
        email = col7.text_input("Email", value=default_email)

        submitted = st.form_submit_button(button_label)

        if submitted:
            if not description or not cep or not street or not number or not city or not state or not contact_name or not phone or not email:
                st.error("Todos os campos são obrigatórios.")
            else:
                if is_edit_mode:
                    result = collect_point_service.update_collect_point(
                        collect_point_id, description, cep, street, number, city, state, contact_name, phone, email)
                else:
                    result = collect_point_service.create_collect_point(
                        description, cep, street, number, city, state, contact_name, phone, email)

                feedback.send_feedback(**result)

    if st.button("Voltar para a Listagem"):
        navigation.goto("collect_point")
