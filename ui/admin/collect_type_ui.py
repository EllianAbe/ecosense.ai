import streamlit as st
from service.collect_type_service import CollectTypeService
from ui.components import feedback
from ui.components import home_button
from navigation import navigation


def page_list_collect_types():
    st.header("Tipos de Coleta Cadastrados")

    collect_type_service = CollectTypeService()

    with st.container(horizontal=True):
        home_button()

        if st.button("Criar Novo Tipo de Coleta"):
            navigation.goto("collect_type/edit")

    collect_types_result = collect_type_service.read_collect_types()

    if collect_types_result['status'] == 'error':
        st.error(collect_types_result['message'])
        return

    collect_types = collect_types_result['data']
    if not collect_types:
        st.info("Nenhum tipo de coleta cadastrado ainda.")
        return

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1, 5, 1, 1.3])

        col1.write("**ID**")
        col2.write("**Descrição**")
        col3.write("**Editar**")
        col4.write("**Deletar**")

    for collect_type in collect_types:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([1, 5, 1, 1.3])

            col1.write(collect_type.id)
            col2.write(collect_type.description)

            if col3.button("Editar", key=f"edit_{collect_type.id}"):
                navigation.goto("collect_type/edit",
                                {'collect_type_id': collect_type.id})

            if col4.button("Deletar", key=f"delete_{collect_type.id}"):
                result = collect_type_service.delete_collect_type(
                    collect_type.id)
                feedback.send_feedback(**result)

                st.rerun()


def page_edit_collect_type():
    collect_type_id = navigation.get_page_args().get('collect_type_id')
    is_edit_mode = collect_type_id is not None
    title = "Editar Tipo de Coleta" if is_edit_mode else "Cadastro de Novo Tipo de Coleta"
    button_label = "Salvar Alterações" if is_edit_mode else "Cadastrar"

    st.header(title)

    collect_type_service = CollectTypeService()

    collect_type_to_edit = None
    if is_edit_mode:
        collect_type_result = collect_type_service.get_collect_type(
            collect_type_id)
        if collect_type_result['status'] == 'error':
            st.error(collect_type_result['message'])
            return
        collect_type_to_edit = collect_type_result['data']

    default_description = collect_type_to_edit.description if collect_type_to_edit else ""

    with st.form("collect_type_form"):
        description = st.text_input(
            "Descrição do Tipo de Coleta", value=default_description)
        submitted = st.form_submit_button(button_label)

        if submitted:
            if not description:
                st.error("O campo 'Descrição' é obrigatório.")
            else:
                if is_edit_mode:
                    result = collect_type_service.update_collect_type(
                        collect_type_id, description)
                else:
                    result = collect_type_service.create_collect_type(
                        description)

                feedback.send_feedback(**result)

    if st.button("Voltar para a Listagem"):
        navigation.goto("collect_type")
