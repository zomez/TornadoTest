from .handlers import RegisterHandler, LoginHandler, RefreshTokenHandler

def get_user_routes(db_session):
    return [
        (r"/user/register", RegisterHandler, dict(db_session=db_session)),  # Передаем db_session
        (r"/user/login", LoginHandler, dict(db_session=db_session)),        # Передаем db_session
        (r"/user/refresh_token", RefreshTokenHandler, dict(db_session=db_session)),  # Передаем db_session
    ]
