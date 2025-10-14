from typing import Dict
from streamlit.navigation.page import StreamlitPage
import streamlit as st

global navigation


class NavigationFacade():
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(NavigationFacade, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if not hasattr(self, 'routes'):
            self.pages = {}

    def register(self, path: str, page_func, is_default: bool = False):
        def run_with_session_state(run_func):
            def wrapper(*args, **kwargs):
                st.session_state.current_page = path
                return run_func(*args, **kwargs)
            return wrapper

        page = st.Page(page_func, default=is_default)
        page.run = run_with_session_state(page.run)

        self.pages[path] = page

    def goto(self, url: str, page_args: Dict = {}):
        st.session_state.page_args = page_args

        page = self.pages[url]

        st.session_state.previous_page = st.session_state.current_page
        st.switch_page(page)

    def get_page_args(self):
        return st.session_state.page_args

    def run(self):
        pg = st.navigation(
            list(self.pages.values()),
            position='top'
        )

        pg.run()


navigation = NavigationFacade()
