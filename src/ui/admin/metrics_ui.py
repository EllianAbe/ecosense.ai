import streamlit as st
from service.metrics_service import MetricsService
import time

metric_service = MetricsService()


def metrics_ui():
    st.title('Metrics')
    st.session_state.files = st.file_uploader('Carregue seu dataset aqui',
                                              accept_multiple_files='directory', type=['jpg', 'jpeg', 'png'])
    st.session_state.setdefault('result', {})

    files = st.session_state.files

    grouped_files = __group_by_subdir(files)

    for group, files in grouped_files.items():
        total = len(files)
        st.write('###', group, f'({total})')
        result = st.session_state['result']
        if st.button('Testar', key='btn_' + group):
            result[group] = []

            total = len(files)

            progress = st.progress(1.0)

            with st.empty():
                for percentage in metric_service.test_data_set(files, result[group]):
                    progress.progress(percentage)

                    time.sleep(6)

        table = [{
            'name': r['name'],
            'descrição': r['description'],
            'tipo': r['collect_type']
        } for r in result.get(group, [])]

        if table:
            st.dataframe(table)


def __group_by_subdir(files):
    grouped_files = {}
    for file in files:
        parts = file.name.split('/')
        if len(parts) >= 3:
            subdir = parts[1]
            grouped_files.setdefault(subdir, []).append(file)
        else:
            grouped_files.setdefault('root', []).append(file)

    return grouped_files
