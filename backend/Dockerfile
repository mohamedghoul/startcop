# ---- backend/Dockerfile ----
FROM python:3.11-slim

# system deps
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    curl \
    procps \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn[standard] watchdog

COPY src/ ./src/
COPY tests/ ./tests/

RUN find . -type d -name "__pycache__" -exec rm -rf {} +

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]