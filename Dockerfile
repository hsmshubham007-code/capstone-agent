FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV EMBEDDING_MODEL=/app/models/all-MiniLM-L6-v2

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --default-timeout=300 \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.14.0

RUN pip install --no-cache-dir \
    --default-timeout=300 \
    --retries=10 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]