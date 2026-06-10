FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# ============================
# DEFINICIÓN DE ARGUMENTOS
# ============================
ARG ENV
ARG DB_ENGINE
ARG DB_USER
ARG DB_PASS
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG SQLITE_PATH
ARG SQLALCHEMY_TEST_URL
ARG SECRET_KEY
ARG ALGORITHM
ARG ACCESS_TOKEN_EXPIRE_MINUTES
ARG DB_SSL_CA

# ============================
# CONVERSIÓN A VARIABLES DE ENTORNO
# ============================
ENV ENV=${ENV}
ENV DB_ENGINE=${DB_ENGINE}
ENV DB_USER=${DB_USER}
ENV DB_PASS=${DB_PASS}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}

ENV SQLITE_PATH=${SQLITE_PATH}
ENV SQLALCHEMY_TEST_URL=${SQLALCHEMY_TEST_URL}

ENV SECRET_KEY=${SECRET_KEY}
ENV ALGORITHM=${ALGORITHM}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
ENV DB_SSL_CA=${DB_SSL_CA}

# ============================

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

RUN adduser --disabled-password fastapiuser
USER fastapiuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

