FROM python:3.11-slim

WORKDIR /app

# Отключаем буферизацию логов, чтобы сразу видеть ошибки в консоли
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Создаем папку для данных
ENV DATA_DIR=/app/data
RUN mkdir -p /app/data && chmod 777 /app/data

# Запускаем скрипт (замените main.py на имя вашего файла, если назовете иначе)
CMD ["python", "main.py"]
