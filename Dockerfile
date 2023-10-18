FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    \
    PROJECT_PATH="/rosatom-sso" \
    VENV_PATH="/rosatom-sso/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


FROM python-base as builder-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        curl \
        build-essential

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR $PROJECT_PATH

COPY poetry.lock pyproject.toml README.md ./
COPY ./migrations ./migrations/
RUN poetry install --compile --sync --only main

COPY ./rosatom_sso ./rosatom_sso/
RUN poetry install --compile --only-root


FROM python-base as production

COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VENV_PATH $VENV_PATH

WORKDIR $PROJECT_PATH
COPY --from=builder-base $PROJECT_PATH/pyproject.toml .

ENTRYPOINT [ "poetry", "run" ]
CMD [ "rosatom-sso" ]
