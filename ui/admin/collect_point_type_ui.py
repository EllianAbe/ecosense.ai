from service.collect_point_service import CollectPointService
from service.collect_point_type_service import CollectPointCollectTypeService
from service.collect_type_service import CollectTypeService
from ui.components import go_back_button
from navigation import navigation
import streamlit as st

collect_point_service = CollectPointService()
collect_type_service = CollectTypeService()
collect_point_collect_type_service = CollectPointCollectTypeService()


def page_collect_point_types():
    collect_point_id = navigation.get_page_args().get('collect_point_id')

    st.header("Gerenciar Tipos de Materiais")

    collect_point_result = collect_point_service.get_collect_point(
        collect_point_id)
    if collect_point_result['status'] == 'error':
        st.error(collect_point_result['message'])
        return
    collect_point = collect_point_result['data']
    st.subheader(f"**Ponto de Coleta:** {collect_point.description}")

    # Fetch all collect types
    collect_types_result = collect_type_service.read_collect_types()
    if collect_types_result['status'] == 'error':
        st.error(collect_types_result['message'])
        return
    collect_types = collect_types_result['data']

    # Fetch existing collect types for this collect point
    existing_relations = collect_point_collect_type_service.read_collect_point_collect_types()

    if existing_relations["status"] == "error":
        st.error(existing_relations["message"])
        return

    existing_relations_data = existing_relations["data"]

    existing_collect_type_ids = [
        relation.collect_type_id for relation in existing_relations_data if relation.collect_point_id == collect_point_id]

    # Display checkboxes for each collect type
    selected_collect_type_ids = []
    st.write("Selecione os tipos de materiais aceitos neste ponto de coleta:")
    for collect_type in collect_types:
        is_selected = collect_type.id in existing_collect_type_ids
        checkbox_label = f"{collect_type.description} (ID: {collect_type.id})"
        is_selected = st.checkbox(checkbox_label, value=is_selected)
        if is_selected:
            selected_collect_type_ids.append(collect_type.id)

    # Update the relationships
    if st.button("Salvar Tipos de Materiais"):
        # Delete existing relations
        for relation in existing_relations_data:
            if relation.collect_point_id == collect_point_id:
                delete_result = collect_point_collect_type_service.delete_collect_point_collect_type(
                    collect_point_id, relation.collect_type_id)
                if delete_result['status'] == 'error':
                    st.error(delete_result['message'])
                    return

        # Create new relations
        for collect_type_id in selected_collect_type_ids:
            create_result = collect_point_collect_type_service.create_collect_point_collect_type(
                collect_point_id, collect_type_id)
            if create_result['status'] == 'error':
                st.error(create_result['message'])
                return

        st.success("Tipos de materiais atualizados com sucesso!")

    go_back_button()
