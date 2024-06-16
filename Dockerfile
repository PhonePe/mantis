FROM --platform=linux/amd64 python:3.12-slim

RUN apt-get update -y && apt-get upgrade -y

# Setup work directory
WORKDIR /home/
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN python -m pip install --upgrade setuptools wheel

# Install Poetry
RUN pip install poetry==1.4.2

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Setup Poetry ENV variables
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* /home/

# Install dependencies using Poetry
RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
COPY . .
EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port 8000 