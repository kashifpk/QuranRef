### Python App build
FROM python:3.12-alpine AS app-build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

# Set the working directory
RUN mkdir /code
WORKDIR /code

# Install system dependencies and Rust (needed for uv)
RUN apk add --no-cache curl build-base

# Install Rust (needed for uv)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy the project files
COPY pyproject.toml README.md /code/
COPY quranref /code/quranref

# Install hatchling and dependencies
RUN uv pip install --system hatchling && \
    uv pip install --system .

# Copy the rest of the files
COPY .env /code/.env
COPY static /code/static

# Create static directory
RUN mkdir -p /code/static

# Install the application
RUN uv pip install --system -e .

# Start prod server
CMD ["python", "-m", "fastapi", "run", "quranref/main.py", "--host", "0.0.0.0", "--port", "8000"]


