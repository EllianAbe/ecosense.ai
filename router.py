import streamlit as st

router = None


class Router:
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(Router, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if not hasattr(self, 'routes'):
            self.routes = {}
            self.default_page = None

    def route(self, page_name: str, is_default: bool = False):
        def decorator(func):
            self.add_route(page_name, func, is_default)
            return func
        return decorator

    def add_route(self, page_name: str, func, is_default: bool = False):
        self.routes[page_name] = func

        if is_default:
            self.default_page = page_name

    def route_to(self, route: str):
        if route not in self.routes:
            raise ValueError(f"Route '{route}' not defined.")

        st.session_state.page = route
        st.rerun()

    def serve(self):
        if 'page' not in st.session_state:
            if self.default_page:
                st.session_state.page = self.default_page
            else:
                st.session_state.page = next(iter(self.routes))

        current_page = st.session_state.page
        handler = self.routes.get(current_page)

        if handler:
            handler()
        else:
            st.error(f"Página '{current_page}' não encontrada.")
            if self.default_page and self.default_page in self.routes:
                self.routes[self.default_page]()


router = Router()
