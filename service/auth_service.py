from service.user_service import UserService

user_service = UserService()


class AuthService():
    def __init__(self):
        pass

    def auth(self, username):
        result = user_service.get_user(username=username)

        if result['status'] == 'success':
            return result['data']

        else:
            return None
