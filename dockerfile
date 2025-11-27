FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    gcc \
    ffmpeg \
    libmagic1 \
    imagemagick \
    chromium \
    libnss3 libnspr4 \
    libxss1 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0 libgtk-3-0 \
    ca-certificates wget unzip \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# README.md* = if present copy else don't
COPY pyproject.toml README.md* ./

RUN pip install --upgrade pip && \
    pip install .


FROM builder as test

ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN pip install .[dev]

RUN pip show moviepy >&2
RUN ruff check .
RUN ruff format --check .

RUN pytest



FROM builder as prod

RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser && \
    chown -R appuser:appuser /home/appuser


WORKDIR /app

COPY --chown=appuser:appuser . .

USER appuser

CMD ["bash", "-c", "cd src && python run.py"]






