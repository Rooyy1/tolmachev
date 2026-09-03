FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Порт, на котором бот принимает вебхуки GetCourse
EXPOSE 8080

CMD ["python", "bot.py"]
