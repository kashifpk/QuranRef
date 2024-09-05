FROM python:3.12-alpine AS py-build

ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy the poetry files
COPY pyproject.toml poetry.lock /app/

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the files
COPY .env /app
COPY quranref /app/quranref

# Install the package
RUN poetry install

# Start dev server
CMD ["poetry", "run", "fastapi", "run", "quranref/main.py", "--host", "0.0.0.0", "--port", "7000"]
