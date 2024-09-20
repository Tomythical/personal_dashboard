FROM python:3.12-slim-bookworm as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV PYTHONUNBUFFERED True
EXPOSE 8080

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY  personal_dashboard/ ./personal_dashboard

ENTRYPOINT ["python", "-m", "streamlit", "run", "/app/personal_dashboard/frontend/dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]