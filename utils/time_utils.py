from datetime import datetime
import pytz

# Задаём московскую временную зону
moscow_tz = pytz.timezone('Europe/Moscow')

def get_current_time():
    """Возвращает текущее время в московской временной зоне."""
    return datetime.now(moscow_tz)