# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем переменные окружения для Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./
COPY flore_bot ./flore_bot
COPY .env ./

# Устанавливаем зависимости через Poetry
RUN poetry install --no-root

# Открываем порт для FastAPI (если нужно)
EXPOSE 8075

# Запускать будем бот (можешь поменять на API, если надо)
CMD ["python", "-m", "flore_bot.run_bot"]
