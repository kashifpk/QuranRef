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
COPY .env /code
COPY quranref /code/quranref

# Install the package
RUN poetry install --only main,dev,test --no-interaction

# Start dev server
CMD ["poetry", "run", "fastapi", "run", "quranref/main.py", "--host", "0.0.0.0", "--port", "7000"]
