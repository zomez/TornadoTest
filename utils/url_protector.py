import jwt
from tornado.web import RequestHandler
from sqlalchemy.orm import Session
from config import SECRET_KEY
from models.user_model import User
from utils.time_utils import get_current_time

class ProtectedHandler(RequestHandler):
    def initialize(self, db_session: Session, required_roles=None):
        self.db_session = db_session
        self.required_roles = required_roles  # Список ролей, которые нужны для доступа к маршруту

    def prepare(self):
        # Получаем access_token из заголовков
        auth_header = self.request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            self.set_status(401)
            self.write({"error": "Требуется авторизация"})
            self.finish()
            return

        access_token = auth_header.split(" ")[1]

        try:
            # Декодируем токен
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            # Проверяем, существует ли пользователь и соответствует ли access_token
            user = self.db_session.query(User).filter(User.id == user_id).first()

            if not user or user.access_token != access_token:
                self.set_status(401)
                self.write({"error": "Неверный или истекший access token"})
                self.finish()
                return

            # Проверяем права доступа пользователя
            if self.required_roles and not self.has_required_role(user):
                self.set_status(403)
                self.write({"error": "Недостаточно прав для доступа"})
                self.finish()
                return

            # Если все проверки пройдены, продолжаем обработку запроса
            self.current_user = user

        except jwt.ExpiredSignatureError:
            self.set_status(401)
            self.write({"error": "Access token истек"})
            self.finish()
        except jwt.InvalidTokenError:
            self.set_status(401)
            self.write({"error": "Неверный access token"})
            self.finish()

    def has_required_role(self, user):
        """Проверяет, есть ли у пользователя необходимая роль"""
        user_roles = {role.name for role in user.roles}  # Список ролей пользователя
        required_roles_set = set(self.required_roles)
        return not required_roles_set.isdisjoint(user_roles)  # Проверка пересечения ролей
