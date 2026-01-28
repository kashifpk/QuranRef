# QuranRef Production Dockerfile
# Builds a single image that serves both API and frontend

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STATIC_DIR=/code/static

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock README.md /code/
COPY quranref /code/quranref

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy static files (frontend build output)
COPY static /code/static

# Expose port
EXPOSE 7000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "quranref.main:app", "--host", "0.0.0.0", "--port", "7000"]
