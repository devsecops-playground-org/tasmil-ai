# syntax=docker/dockerfile:1

# ---- build -----------------------------------------------------------------
FROM python:3.12.11-slim AS builder

ENV POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && python -m venv /opt/venv

WORKDIR /build

# Dependencies first: application edits do not invalidate this layer.
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

COPY app ./app

# ---- runtime ---------------------------------------------------------------
FROM python:3.12.11-slim AS runtime

ARG GIT_SHA=unknown
LABEL org.opencontainers.image.source="https://github.com/devsecops-playground-org/tasmil-ai" \
      org.opencontainers.image.revision="${GIT_SHA}"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --no-create-home app

WORKDIR /srv
COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --chown=app:app app ./app

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
