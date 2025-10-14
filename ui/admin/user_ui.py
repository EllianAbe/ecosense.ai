import streamlit as st
from db.models import UserPosition
from service.user_service import UserService
from ui.components import go_back_button
from ui.components.feedback import send_feedback
from navigation import navigation

user_service = UserService()


def page_list_users():
    st.header("Usuários Cadastrados")

    col1, col2, _ = st.columns([1.5, 3, 8.5])

    with col1:
        go_back_button()

    with col2:
        if st.button("Criar Novo Usuário"):
            navigation.goto("user/edit")

    users_result = user_service.read_users()
    if users_result['status'] == 'error':
        st.error(users_result['message'])
        st.stop()

    users = users_result['data']
    if not users_result:
        st.info("Nenhum usuário cadastrado ainda.")
        st.stop()

    # Cabeçalhos da tabela

    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 1.3])

        col1.write("**ID**")
        col2.write("**Descrição**")
        col3.write("**Posição**")
        col4.write("**Ações**")

    # Exibe cada usuário em uma linha
    for user in users:
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 1.3])

            col1.write(user.id)
            col2.write(user.username)
            col3.write(user.position.value)

            if col4.button("Editar", key=f"edit_{user.id}"):
                navigation.goto("user/edit", {'user_id': user.id})

            if col5.button("Deletar", key=f"delete_{user.id}"):
                user_service.delete_user(user.id)
                st.rerun()


def page_edit_user():
    user_id = navigation.get_page_args().get('user_id')

    is_edit_mode = user_id is not None
    title = "Editar Usuário" if is_edit_mode else "Cadastro de Novo Usuário"
    button_label = "Salvar Alterações" if is_edit_mode else "Cadastrar"

    st.header(title)

    user_to_edit = None

    if is_edit_mode:
        result = user_service.get_user(user_id)

        if result['status'] == 'success':
            user_to_edit = result['data']
        else:
            send_feedback(**result)

    default_description = user_to_edit.username if user_to_edit else ""
    positions = [pos.value for pos in UserPosition]
    default_position_index = positions.index(
        user_to_edit.position.value) if user_to_edit else 0

    with st.form("user_form"):
        description = st.text_input(
            "Descrição do Usuário", value=default_description)
        position = st.selectbox(
            "Posição",
            positions,
            index=default_position_index
        )
        submitted = st.form_submit_button(button_label)

        if submitted:
            if not description:
                st.error("O campo 'Descrição' é obrigatório.")
            else:
                if is_edit_mode:
                    result = user_service.update_user(
                        user_id, description, position)
                else:
                    result = user_service.create_user(description, position)

                send_feedback(**result)

    if st.button("Voltar para a Listagem"):
        navigation.goto("user")
