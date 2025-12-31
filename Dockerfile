FROM python:3.11-slim

WORKDIR /app

# Копируем pyproject.toml
COPY pyproject.toml .

# Устанавливаем проект со всеми зависимостями
RUN pip install --no-cache-dir .

# Копируем весь код
COPY . .

# Запускаем бота
CMD ["python3", "tg_activate_bot.py"]