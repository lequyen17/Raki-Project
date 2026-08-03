FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["sh", "-c", "until python -c 'import socket; s = socket.socket(); s.connect((\"chat-db\", 5432))' 2>/dev/null; do echo 'Đang chờ chat-db...'; sleep 1; done; uvicorn app.main:app --host 0.0.0.0 --port 8000"]