import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy.orm import declarative_base

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Теперь мы можем импортировать config
from config import DATABASE_URL  # Импортируйте вашу конфигурацию

# Импорт моделей
from models.user_model import Base  # Импортируйте базовый класс моделей

# Настройка конфигурации
config = context.config
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Настройка логирования из файла конфигурации
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()