import tornado.ioloop
import tornado.web
from sqlalchemy.orm import sessionmaker

from build.create_defalt_role import create_default_roles

from config import PORT
from models.db import engine
from models.user_model import Base
from user.routes import get_user_routes

Session = sessionmaker(bind=engine)

class Application(tornado.web.Application):
    def __init__(self):
        db_session = Session()  # Создаем экземпляр сессии
        # Передаем db_session в каждый маршрут
        handlers = get_user_routes(db_session)
        super(Application, self).__init__(handlers)


if __name__ == "__main__":
    # Создание таблиц в базе данных (если они еще не созданы)
    Base.metadata.create_all(bind=engine)
    # Создание стандартных ролей
    db_session = Session()
    create_default_roles(db_session)
    # Запуск приложения
    app = Application()
    app.listen(PORT)

    # Печатаем сообщение о старте сервера
    print(f"Сервер Tornado запущен на http://localhost:{PORT}")

    # Запуск цикла обработки событий Tornado
    tornado.ioloop.IOLoop.current().start()
