from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Создание фабрики сессий
SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Используем scoped_session для потокобезопасности
Session = scoped_session(SessionFactory)

# Функция для получения сессии базы данных
def get_db():
    """Создает сессию базы данных и проверяет подключение."""
    db = Session()
    try:
        # Пробуем выполнить простой запрос для проверки подключения
        #db.execute('SELECT 1')
        print("Подключение к базе данных установлено успешно.")
        yield db
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
    finally:
        db.close()