FROM python:3.12-alpine AS base

WORKDIR /app

ENV VIRTUAL_ENV=/venv/ \
    \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1 \
    POETRY_NO_CACHE=1 \
    \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY ./src/ ./src/
COPY pyproject.toml poetry.lock README.md LICENSE ./

FROM base as build-and-install

RUN python -m venv $VIRTUAL_ENV

ARG POETRY_VERSION=1.8.2

RUN pip install poetry==${POETRY_VERSION}

RUN poetry install -E speedups  # poetry will install in $VIRTUAL_ENV because it thinks we are using virtualenv https://github.com/python-poetry/poetry/blob/2ad0d938854fae3c5e3e8b49e4414cef4687fb60/src/poetry/utils/env/env_manager.py#L289

FROM base AS runtime

COPY --from=build-and-install /venv/ /venv/

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

STOPSIGNAL SIGINT
ENTRYPOINT ["python", "-m"]
CMD ["_docker_stub"]
