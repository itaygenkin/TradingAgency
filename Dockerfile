FROM python:3.11-slim

# set environment variables to optimize python execution in docker
ENV PYTHONDOWTWRITETYPECODE=1 \
    PYTHONUNBUFFERED=1 \

WORKDIR /app

# install system dependencies required for PostgreSQL (psycopg2) and building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code
COPY . .