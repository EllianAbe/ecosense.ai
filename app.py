from ui.account import first_access_ui, login_ui
from ui.admin import collect_point_ui, collect_type_ui, user_ui, collect_point_type_ui, chatbot_ui
from ui import home_ui
from navigation import navigation
from db.database import init_db

init_db()

navigation.register('login', login_ui.page_login, is_default=True)
navigation.register('first_access', first_access_ui.page_first_access)
navigation.register('home', home_ui.page_home)
navigation.register('user', user_ui.page_list_users)
navigation.register('user/edit', user_ui.page_edit_user)
navigation.register('collect_type', collect_type_ui.page_list_collect_types)
navigation.register('collect_type/edit',
                    collect_type_ui.page_edit_collect_type)
navigation.register(
    'collect_point', collect_point_ui.page_list_collect_points)
navigation.register('collect_point/edit',
                    collect_point_ui.page_edit_collect_point)
navigation.register('collect_point/types',
                    collect_point_type_ui.page_collect_point_types)


# ...after other pages
navigation.register('chatbot', chatbot_ui.page_chatbot)

navigation.run()
