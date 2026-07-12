ARG PYTHON_VERSION=3.13.14
ARG UV_VERSION=0.11.27

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION}-alpine AS build
COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:${PYTHON_VERSION}-alpine AS final
RUN adduser -D app
WORKDIR /app

COPY --from=build --chown=app:app /app/.venv ./.venv
COPY --chown=app:app src/ ./src/

USER app

EXPOSE 8000
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '8000') + '/utils/health')"]

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir src"]
