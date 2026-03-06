FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY db ./db

ENV HOST=0.0.0.0
ENV PORT=8080
CMD ["sh", "-c", "python -m uvicorn app.main:app --host ${HOST} --port ${PORT}"]