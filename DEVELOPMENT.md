# QuranRef Development Guide

This guide provides instructions for setting up and running QuranRef in different development environments.

## Prerequisites

### For Docker Development (Recommended)
- Docker and Docker Compose
- That's it! All other dependencies are containerized

### For Direct Host Development
- Python 3.12+
- uv (Python package installer) - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Bun (JavaScript runtime) - Install: `curl -fsSL https://bun.sh/install | bash`
- ArangoDB 3.8.9+
- Docker (optional, for database only)

## Development Approaches

### Recommended: Docker Development
**Best for:** Most developers, consistent environment, quick start
- All dependencies pre-configured
- System-upgrade-proof
- Matches production environment
- Hot-reload optimized

### Alternative: Direct Host Development  
**Best for:** Advanced debugging, custom tooling integration
- Requires manual dependency installation
- Direct access to processes
- Faster iteration for backend changes

## Docker Development (Recommended)

### Quick Start

```bash
# Start all services with one command
./dev-docker.sh up

# Access services:
# Frontend: http://localhost:41149 (with hot-reload)
# Backend: http://localhost:41148 (with auto-reload)
# ArangoDB: http://localhost:18529
```

### Docker Development Commands

```bash
# Start services
./dev-docker.sh up       # Start all services
./dev-docker.sh logs     # View logs
./dev-docker.sh down     # Stop all services

# Development tasks
./dev-docker.sh shell    # Access backend container
./dev-docker.sh build    # Rebuild after dependency changes

# Inside backend container
pytest                   # Run tests
ruff check              # Lint code
quranref-cli --help     # CLI commands
```

### Frontend Development in Docker

```bash
# Frontend auto-starts with hot-reload
# Edit files in frontend/src/ - changes appear instantly

# Run frontend commands
docker exec quranref_frontend_dev bun run build
docker exec quranref_frontend_dev vue-tsc -b
```

## Direct Host Development

### Setting up the Backend

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Install dependencies with uv:

   ```bash
   uv sync
   ```

3. Start the backend development server:

   ```bash
   uv run fastapi dev quranref/main.py --host 0.0.0.0 --port 8000
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

### Database Setup (Both Approaches)

After starting services, initialize the database:

```bash
# For Docker
./dev-docker.sh shell
# Then run inside container:
quranref-cli db init
quranref-cli db populate-surahs
quranref-cli db import-text
quranref-cli post-process link-ayas-to-surahs
quranref-cli post-process make-words

# For Direct Host
cd backend
uv run quranref-cli db init
uv run quranref-cli db populate-surahs
uv run quranref-cli db import-text
uv run quranref-cli post-process link-ayas-to-surahs
uv run quranref-cli post-process make-words
```

## Package Management

### Backend - Python with uv

The backend uses `uv` for ultra-fast Python dependency management:

```bash
cd backend

# Install/sync dependencies from pyproject.toml
uv sync

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Run commands with uv
uv run python script.py
uv run pytest
uv run fastapi dev
```

### Frontend - JavaScript with Bun

The frontend uses `bun` for fast JavaScript package management:

```bash
cd frontend

# Install dependencies from package.json
bun install

# Add a new dependency
bun add package-name

# Add a development dependency
bun add -d package-name

# Run scripts
bun run dev
bun run build
bun test
```

### Why uv and Bun?

**uv advantages:**
- 10-100x faster than pip
- Built-in virtual environment management
- Consistent dependency resolution
- Drop-in replacement for pip

**Bun advantages:**
- Faster than npm/yarn/pnpm
- Built-in TypeScript support
- Native speed JavaScript runtime
- Compatible with npm packages

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
