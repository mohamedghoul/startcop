FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY src/ ./src/
COPY tests/ ./tests/

EXPOSE 3000

CMD pytest tests && uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload