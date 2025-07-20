# QuranRef Development Guide

This guide provides instructions for setting up and running QuranRef in different development environments.

## Prerequisites

- Python 3.12+
- uv (Python package installer)
- Bun (for frontend development)
- ArangoDB 3.8.9+
- Podman (optional, for containerized development)

## Development Options

You have three options for development:

1. **Direct Host Development** - Run all components directly on your host machine
2. **Podman Containerized Development** - Run components in Podman containers
3. **Docker Containerized Development** - Run components in Docker containers (see docker-compose files)

## 1. Direct Host Development

### Setting up the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies with uv:
   ```bash
   uv pip install -e .
   ```

3. Start the backend development server:
   ```bash
   python -m fastapi dev quranref/main.py --host 0.0.0.0 --port 8000
   ```

### Setting up the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies with Bun:
   ```bash
   bun install
   ```

3. Start the development server:
   ```bash
   bun run dev
   ```

### Setting up ArangoDB

1. Install ArangoDB on your system
2. Start ArangoDB server:
   ```bash
   arangod --server.endpoint tcp://0.0.0.0:8529
   ```

## 2. Podman Containerized Development

### Starting all services

1. From the project root, run:
   ```bash
   podman-compose -f podman-compose.yml up
   ```

### Starting individual services

1. Start ArangoDB:
   ```bash
   podman-compose -f podman-compose.yml up arangodb
   ```

2. Start backend:
   ```bash
   podman-compose -f podman-compose.yml up backend
   ```

3. Start frontend:
   ```bash
   podman-compose -f podman-compose.yml up frontend
   ```

### Building and rebuilding images

```bash
podman-compose -f podman-compose.yml build
```

To rebuild a specific service:
```bash
podman-compose -f podman-compose.yml build <service-name>
```

### Accessing Services

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- ArangoDB UI: http://localhost:8529

## Converting from Poetry to uv

If you're converting an existing Poetry project to use uv, you can use the included conversion script:

```bash
./convert-to-uv.sh
```

This script will:
1. Convert your Poetry dependencies to a standard requirements.txt
2. Create a uv-compatible pyproject.toml file
3. Back up your original Poetry files
4. Install the project in development mode

### Key differences in pyproject.toml

The updated pyproject.toml file uses the standard PEP 621 format:

- Uses `[project]` instead of `[tool.poetry]`
- Uses `[project.optional-dependencies]` instead of `[tool.poetry.group.*.dependencies]`
- Uses `[project.scripts]` instead of `[tool.poetry.scripts]`
- Uses hatchling as the build backend instead of poetry-core

### Required packages

When using uv with this project setup, you'll need:

- `hatchling`: Modern Python build backend (equivalent to setuptools but more modern)
- `pyproject-metadata`: Used during conversion to extract Poetry dependencies

These are automatically installed by the conversion script.

## Debugging

### Backend Debugging

When running directly on the host, you can use Python debugging techniques:

1. Add breakpoints in your code:
   ```python
   import debugpy
   # ...
   debugpy.breakpoint()
   # or use standard Python breakpoint()
   breakpoint()
   ```

2. Use VS Code debugging configuration:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "FastAPI",
         "type": "python",
         "request": "launch",
         "module": "fastapi",
         "args": ["dev", "quranref/main.py", "--host", "0.0.0.0", "--port", "8000"],
         "cwd": "${workspaceFolder}/backend",
         "justMyCode": false
       }
     ]
   }
   ```

### Frontend Debugging

1. Use browser developer tools
2. Use Vue Devtools extension
3. Add source maps for better debugging

## Environment Variables

- Backend environment variables are stored in `backend/.env`
- Frontend environment variables are stored in `frontend/.env`

Make sure to set appropriate values for both environments.