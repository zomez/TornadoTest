import os

settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True,  # Включаем режим отладки для разработки
    "cookie_secret": "YOUR_SECRET_KEY",  # Для работы с сессиями (если нужно)
}
# Порт на котором стартуем
PORT = 8888

# Конфигурации для JWT
JWT_SECRET = "YOUR_JWT_SECRET"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # Время жизни токена — 1 час

DATABASE_URL = "postgresql://postgres:password@localhost:5433/mydatabase"
SECRET_KEY = "12345AAA"
REFRESH_SECRET_KEY = "12345AAB"