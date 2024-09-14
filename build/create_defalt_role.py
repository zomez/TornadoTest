from models.user_model import Role


def create_default_roles(db_session):
    """Создание стандартных ролей при первой инициализации базы данных"""
    default_roles = [
        {"name": "Admin", "help_text": "Администратор"},
        {"name": "Manager", "help_text": "Менеджер"},
        {"name": "Operator", "help_text": "Оператор"},
        {"name": "Worker", "help_text": "Работник"},
        {"name": "Responsible", "help_text": "Ответственный"}
    ]

    # Проверка, существуют ли роли в базе данных
    existing_roles = db_session.query(Role).count()

    if existing_roles == 0:
        # Если роли ещё не созданы, добавляем их
        for role_data in default_roles:
            role = Role(name=role_data["name"], help_text=role_data["help_text"])
            db_session.add(role)
        db_session.commit()
        print("Стандартные роли успешно созданы.")
    else:
        print("Роли уже существуют в базе данных.")