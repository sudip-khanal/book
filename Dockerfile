# Pull base image
FROM python:3.12.5-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock /app/
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade --no-cache-dir pip poetry \
    && poetry --version \
    # Configure Poetry to use system site packages instead of virtualenv
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip uninstall -y poetry virtualenv-clone virtualenv

# Copy project
COPY . .

