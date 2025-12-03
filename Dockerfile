FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/

RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev

COPY . /app

ENV DJANGO_SETTINGS_MODULE=config.settings

RUN uv run pip install gunicorn

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3"]

