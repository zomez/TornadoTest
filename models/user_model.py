from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from utils.time_utils import get_current_time  # Импортируем нашу функцию


Base = declarative_base()


# Таблица связывания пользователей и ролей (many-to-many)
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Таблица связывания пользователей и отделов (many-to-many)
user_departments = Table(
    'user_departments',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),  # Внешний ключ на пользователей
    Column('department_id', Integer, ForeignKey('departments.id'), primary_key=True)  # Внешний ключ на отделы
)


# Таблица для хранения информации о логах входа пользователей
class UserLoginHistory(Base):
    __tablename__ = 'user_login_history'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Идентификатор записи
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Внешний ключ на пользователя
    login_time = Column(DateTime, default=get_current_time, nullable=False)  # Время входа (по умолчанию текущее время)
    ip_address = Column(String(45))  # IP-адрес пользователя при входе (IPv4 или IPv6)
    user_agent = Column(String(200))  # Информация о браузере/устройстве пользователя

    # Связь с объектом User (один пользователь может иметь много записей о входах)
    user = relationship("User", back_populates="login_history")

    def __repr__(self):
        return f"<UserLoginHistory(user_id={self.user_id}, login_time={self.login_time}, ip_address={self.ip_address})>"


class Role(Base):
    """Модель для хранения ролей пользователей, таких как администратор, менеджер и т.д."""

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # Уникальное имя роли
    help_text = Column(String(255), nullable=False)  # Описание роли на русском языке
    is_active = Column(Boolean, default=True)  # Флаг, указывающий, активна ли роль (True) или отключена (False)

    def __repr__(self):
        return f"<Role(name={self.name}, help_text={self.help_text}, is_active={self.is_active})>"


class Division(Base):
    """Модель для хранения подразделений, которые могут быть связаны с отделами."""

    __tablename__ = 'divisions'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Идентификатор подразделения
    name = Column(String(100), nullable=False)  # Название подразделения
    is_active = Column(Boolean, default=True)  # Флаг, указывающий, активно ли подразделение

    def __repr__(self):
        return f"<Division(name={self.name}, is_active={self.is_active})>"


class Department(Base):
    """Модель для хранения отделов, которые могут быть связаны с пользователями и подразделениями."""

    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Идентификатор отдела
    name = Column(String(100), nullable=False)  # Название отдела
    is_active = Column(Boolean, default=True)  # Флаг, указывающий, активен ли отдел
    division_id = Column(Integer, ForeignKey('divisions.id'))  # Внешний ключ на подразделение
    division = relationship("Division")  # Связь с объектом Division (одно подразделение может быть у отдела)

    def __repr__(self):
        return f"<Department(name={self.name}, is_active={self.is_active}, division={self.division.name})>"


class User(Base):
    """Модель для хранения информации о пользователях системы."""

    __tablename__ = 'users'

    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)  # Идентификатор пользователя
    email = Column(String(100), unique=True,
                   nullable=False)  # Email используется как логин пользователя, должен быть уникальным
    password = Column(String(1000), nullable=False)  # Хэшированный пароль пользователя
    first_name = Column(String(50), nullable=False)  # Имя пользователя (обязательное поле)
    last_name = Column(String(50), nullable=False)  # Фамилия пользователя (обязательное поле)
    middle_name = Column(String(50))  # Отчество (необязательное поле)
    phone = Column(String(20))  # Номер телефона пользователя (необязательное поле)
    # АВТОРИЗАЦИЯ
    access_token = Column(String(255), nullable=True)  # Храним access token
    refresh_token = Column(String(255), nullable=True)  # Храним refresh token

    # Новые поля
    is_active = Column(Boolean, default=True)  # Флаг, указывающий, активен ли пользователь (True) или отключен (False)
    registered_at = Column(DateTime,default=get_current_time)  # Дата и время регистрации пользователя (по умолчанию текущее время)
    last_login = Column(
        DateTime)  # Дата и время последнего входа пользователя в систему (может быть пустым до первого входа)

    # Связь many-to-many с отделами
    departments = relationship("Department",
                               secondary=user_departments)  # Один пользователь может быть связан с несколькими отделами

    # Связь many-to-many с ролями
    roles = relationship("Role",
                         secondary=user_roles)  # Один пользователь может иметь много ролей, и одна роль может принадлежать многим пользователям

    # Связь one-to-many с логами входов
    login_history = relationship("UserLoginHistory", back_populates="user")  # Связь с таблицей логов входов

    def __repr__(self):
        return f"<User(email={self.email}, name={self.first_name} {self.last_name})>"
