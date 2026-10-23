# Используем официальный легкий образ Python 3.11
FROM python:3.11-slim

# Настраиваем часовой пояс сервера внутри контейнера на МСК
ENV TZ=Europe/Moscow
ENV PYTHONUNBUFFERED=1

# Создаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта в контейнер
COPY . .

# Запускаем нашего бота
CMD ["python", "main.py"]
