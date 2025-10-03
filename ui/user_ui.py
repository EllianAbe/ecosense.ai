import streamlit as st
from db.models import UserPosition
from service.user_service import UserService
from ui.components import home_button
from ui.feedback import send_feedback
from router import router

user_service = UserService()


def page_list_users():
    st.header("Usuários Cadastrados")

    home_button()

    if st.button("Criar Novo Usuário"):
        router.route_to("user/edit")

    users_result = user_service.read_users()
    if users_result['status'] == 'error':
        st.error(users_result['message'])
        return

    users = users_result['data']
    if not users_result:
        st.info("Nenhum usuário cadastrado ainda.")
        return

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
                st.session_state.user_id_to_edit = user.id
                router.route_to("user/edit")

            if col5.button("Deletar", key=f"delete_{user.id}"):
                user_service.delete_user(user.id)
                st.rerun()


def page_edit_user():
    user_id = st.session_state.get('user_id_to_edit')

    is_edit_mode = user_id is not None
    title = "Editar Usuário" if is_edit_mode else "Cadastro de Novo Usuário"
    button_label = "Salvar Alterações" if is_edit_mode else "Cadastrar"

    st.header(title)

    user_to_edit = None
    if is_edit_mode:
        user_to_edit = user_service.get_user(user_id)
        if not user_to_edit:
            st.error("Usuário não encontrado.")
            return

    default_description = user_to_edit.description if user_to_edit else ""
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
        router.route_to("user")
