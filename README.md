# Quran Reference

Online easily accessible searchable reference of the Holy Quran and its translations.

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── quranref/         # Application code
│   ├── data/             # Data files
│   ├── tests/            # Backend tests
│   ├── .env              # Backend environment variables
│   ├── Dockerfile        # Backend production Dockerfile
│   ├── Dockerfile.podman # Backend podman Dockerfile
│   └── pyproject.toml    # Python dependencies (uv/hatchling compatible)
├── frontend/             # Vue.js frontend
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   ├── .env              # Frontend environment variables
│   ├── tsconfig.*.json   # TypeScript configuration
│   ├── vite.config.ts    # Vite configuration
│   ├── Dockerfile        # Frontend production Dockerfile
│   ├── Dockerfile.podman # Frontend podman Dockerfile
│   ├── Dockerfile-dev    # Frontend development Dockerfile
│   ├── package.json      # Frontend dependencies
│   └── bun.lockb         # Frontend lock file
├── config/               # Configuration files
│   ├── nginx.conf        # Nginx configuration
│   ├── .env.example      # Example environment variables
│   └── .env.prod         # Production environment variables
├── docker-compose.yml    # Docker compose configuration
├── docker-compose-dev.yml # Development Docker compose
├── docker-compose.prod.yml # Production Docker compose
├── podman-compose.yml    # Podman compose configuration
├── convert-to-uv.sh      # Script to convert from Poetry to uv
├── dev.sh                # Script for direct host development
├── DEVELOPMENT.md        # Detailed development guide
└── README.md             # Project documentation
```

## Development Options

You have three options for developing this project:

1. **Direct Host Development** - Run services directly on your machine
2. **Podman Development** - Run services in Podman containers
3. **Docker Development** - Run services in Docker containers

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed instructions on all development options.

## Quick Start

### Option 1: Direct Host Development

1. Start all services directly on your host:
```bash
./dev.sh all
```

2. Access the services:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - ArangoDB: http://localhost:8529

### Option 2: Podman Development

1. Start the development environment with Podman:
```bash
podman-compose -f podman-compose.yml up
```

2. Access the services (same as direct host).

### Option 3: Docker Development

1. Start the development environment with Docker:
```bash
docker compose -f docker-compose-dev.yml up --build
```

2. Access the services (same as direct host).

## Python Development

This project uses `uv` as the Python package manager (replacing Poetry):

```bash
# Install dependencies
cd backend
uv pip install -e .

# Run the development server
python -m fastapi dev quranref/main.py --host 0.0.0.0 --port 8000
```

If migrating from Poetry, use the provided conversion script:
```bash
./convert-to-uv.sh
```

## Frontend Development

Frontend uses Bun and Vue.js:

```bash
# Install dependencies
cd frontend
bun install

# Start development server
bun run dev
```

## Production Deployment

1. Build the production images:
```bash
docker compose -f docker-compose.prod.yml build
```

2. Deploy the stack:
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Backend (.env)
- `DB_HOSTS`: ArangoDB connection string
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `ENVIRONMENT`: Development/production setting
- `DEBUG`: Debug mode flag

### Frontend (.env)
- `STATIC_URL`: URL for static assets
- `VITE_API_BASE_URL`: Base URL for API requests
- `VITE_WEBSITE_BASE_URL`: Base URL for the website

## Directory-Specific Documentation

- See [backend/README.md](backend/README.md) for backend-specific details
- See [frontend/README.md](frontend/README.md) for frontend-specific details
- See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development instructions
