from router import router
from db.database import init_db
from ui import login_ui, user_ui, collect_type_ui, collect_point_ui, home_ui, first_access_ui


init_db()

router.add_route('login', login_ui.page_login, is_default=True)
router.add_route('first_access', first_access_ui.page_first_access)
router.add_route('home', home_ui.page_home)
router.add_route('user', user_ui.page_list_users)
router.add_route('user/edit', user_ui.page_edit_user)
router.add_route('collect_type', collect_type_ui.page_list_collect_types)
router.add_route('collect_type/edit', collect_type_ui.page_edit_collect_type)
router.add_route('collect_point', collect_point_ui.page_list_collect_points)
router.add_route('collect_point/edit',
                 collect_point_ui.page_edit_collect_point)

if __name__ == "__main__":
    router.serve()
