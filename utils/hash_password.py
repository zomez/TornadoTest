import bcrypt

def hash_password(password):
    # Генерация соли и хеширование пароля
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  # Преобразуем хеш в строку перед сохранением
