# используем официальный легкий образ Python
FROM python:3.11-slim

# запрещаем питону писать файлы .pyc и буферизовать логи
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь остальной код проекта
COPY . .



