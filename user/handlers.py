import jwt
import bcrypt
import json
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from config import SECRET_KEY, REFRESH_SECRET_KEY
from models.db import get_db
from models.user_model import User, UserLoginHistory
from sqlalchemy.orm import Session
from tornado.web import RequestHandler

from utils.hash_password import hash_password
from utils.time_utils import get_current_time


# Время жизни JWT токена (например, 1 час)
TOKEN_EXPIRATION = timedelta(hours=1)

# Секретные ключи для подписывания токенов
#SECRET_KEY = "your_access_token_secret"
#REFRESH_SECRET_KEY = "your_refresh_token_secret"


class AuthMiddleware:
    @staticmethod
    def authenticate_request(handler):
        """Проверка токена JWT в заголовках"""
        auth_header = handler.request.headers.get("Authorization", None)
        if not auth_header:
            handler.set_status(401)
            handler.write({"error": "Требуется авторизация"})
            handler.finish()
            return False

        try:
            # Токен передается в формате "Bearer <token>"
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            handler.current_user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            handler.set_status(401)
            handler.write({"error": "Токен истек"})
            handler.finish()
            return False
        except jwt.InvalidTokenError:
            handler.set_status(401)
            handler.write({"error": "Неверный токен"})
            handler.finish()
            return False

        return True

class RegisterHandler(RequestHandler):
    def initialize(self, db_session: Session):
        self.db_session = db_session

    def post(self):
        print(self.request.body)
        """Регистрация нового пользователя"""
        try:
            # Получаем данные из тела запроса
            data = json.loads(self.request.body)
            email = data.get("email")
            password = data.get("password")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone = data.get("phone", None)  # Телефон может быть необязательным
            print(email, password, first_name, last_name, phone)
            # Простая валидация
            if not email or not password or not first_name or not last_name:
                self.set_status(400)
                self.write({"error": "Все обязательные поля должны быть заполнены"})
                return

            # Хешируем пароль перед сохранением в базу
            hashed_password = hash_password(password)

            # Создаем нового пользователя
            new_user = User(
                email=email,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                is_active=False
            )

            # Сохраняем пользователя в базе данных
            db = next(get_db())
            db.add(new_user)
            db.commit()

            # Отправляем успешный ответ
            self.set_status(201)
            self.write({"message": "Пользователь успешно зарегистрирован", "user_id": new_user.id})

        except IntegrityError:
            # Ошибка при попытке добавить пользователя с существующим email
            self.set_status(409)  # Конфликт
            self.write({"error": "Пользователь с таким email уже существует"})

        except Exception as e:
            print(e)
            # Обрабатываем другие возможные ошибки
            self.set_status(500)
            self.write({"error": str(e)})


# Время жизни токенов
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=15)  # Access token живёт 15 минут
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)     # Refresh token живёт 7 дней

class LoginHandler(RequestHandler):
    def initialize(self, db_session: Session):
        self.db_session = db_session

    def set_access_token(self, user_id):
        """Создаёт access token с кратким сроком действия"""
        expiration = get_current_time() + ACCESS_TOKEN_EXPIRATION
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def set_refresh_token(self, user_id):
        """Создаёт refresh token с долгим сроком действия"""
        expiration = get_current_time() + REFRESH_TOKEN_EXPIRATION
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm="HS256")
        return token

    async def post(self):
        # Получаем данные из тела запроса
        data = json.loads(self.request.body)
        email = data.get("email")
        password = data.get("password")

        # Поиск пользователя по email
        user = self.db_session.query(User).filter(User.email == email).first()

        # Проверка пароля
        if not user or not self.verify_password(password, user.password):
            self.set_status(401)
            self.write({"error": "Неправильный email или пароль"})
            return

        # Обновляем поле last_login
        user.last_login = get_current_time()

        # Генерация новых токенов
        access_token = self.set_access_token(user.id)
        refresh_token = self.set_refresh_token(user.id)

        # Сохраняем access и refresh токены в базе данных
        user.access_token = access_token
        user.refresh_token = refresh_token
        self.db_session.commit()

        # Возвращаем токены пользователю
        self.write({
            "access_token": access_token,
            "refresh_token": refresh_token
        })


class RefreshTokenHandler(RequestHandler):
    def initialize(self, db_session: Session):
        self.db_session = db_session

    def set_access_token(self, user_id):
        """Создаёт новый access token с коротким сроком действия"""
        expiration = get_current_time() + ACCESS_TOKEN_EXPIRATION
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token

    def set_refresh_token(self, user_id):
        """Создаёт новый refresh token с долгим сроком действия"""
        expiration = get_current_time() + REFRESH_TOKEN_EXPIRATION
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm="HS256")
        return token

    async def post(self):
        try:
            # Получаем данные из тела запроса (refresh_token)
            data = json.loads(self.request.body)
            refresh_token = data.get("refresh_token")

            if not refresh_token:
                self.set_status(400)
                self.write({"error": "Refresh token отсутствует"})
                return

            # Декодируем refresh token и получаем user_id
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            # Ищем пользователя по user_id
            user = self.db_session.query(User).filter(User.id == user_id).first()

            # Проверяем, соответствует ли refresh_token
            if not user or user.refresh_token != refresh_token:
                self.set_status(401)
                self.write({"error": "Неверный или недействительный refresh token"})
                return

            # Генерируем новый access и refresh токены
            new_access_token = self.set_access_token(user_id)
            new_refresh_token = self.set_refresh_token(user_id)

            # Обновляем access_token и refresh_token в базе данных
            user.access_token = new_access_token
            user.refresh_token = new_refresh_token
            self.db_session.commit()

            # Возвращаем новые токены
            self.write({
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            })

        except jwt.ExpiredSignatureError:
            self.set_status(401)
            self.write({"error": "Refresh token истек"})
        except jwt.InvalidTokenError:
            self.set_status(401)
            self.write({"error": "Неверный refresh token"})
