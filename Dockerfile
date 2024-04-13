FROM python:3.10.13-alpine3.18

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME="/etc/poetry" \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    POETRY_VERSION=1.8.0

WORKDIR /usr/src/app

COPY . .

RUN apk update \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install \
    && pip uninstall -y poetry \
    && rm -rf /home/appuser/.cache \
    && rm -rf $POETRY_CACHE_DIR \
    && rm -rf /usr/src/app/{__pycache__,admin} \
    && adduser -D appuser \
    && chown -R appuser:appuser .


USER appuser

CMD python -m bot

