### Bun JS build
FROM oven/bun:1 AS js-build

WORKDIR /js-build
COPY bun.lockb .
COPY package.json .

RUN bun install --frozen-lockfile

COPY *.json .
COPY *.js .

COPY js ./js
COPY prod_env .env

RUN bun run build

### Python App build
FROM python:3.12-alpine AS app-build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/usr/local

# Set the working directory
RUN mkdir /code
WORKDIR /code

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy the poetry files
COPY pyproject.toml poetry.lock /code/

RUN poetry config virtualenvs.in-project false
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.path /usr/local

# Install the dependencies
RUN poetry install --only main,dev,test --no-root --no-interaction

# Copy the rest of the files
COPY prod_env /code/.env
COPY quranref /code/quranref
COPY static /code/static

# Copy the JS build
COPY --from=js-build /js-build/static/* /code/static

# Install the package
RUN poetry install --only main,dev,test --no-interaction

# Start prod server
CMD ["poetry", "run", "fastapi", "run", "quranref/main.py", "--host", "0.0.0.0", "--port", "7000"]


