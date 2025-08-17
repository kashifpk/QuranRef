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
│   └── pyproject.toml    # Python dependencies (uv/hatchling compatible)
├── frontend/             # Vue.js frontend
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   ├── .env              # Frontend environment variables
│   ├── tsconfig.*.json   # TypeScript configuration
│   ├── vite.config.ts    # Vite configuration
│   ├── Dockerfile        # Frontend production Dockerfile
│   ├── Dockerfile-dev    # Frontend development Dockerfile
│   ├── package.json      # Frontend dependencies (Bun)
│   └── bun.lockb         # Bun lock file
├── config/               # Configuration files
│   ├── nginx.conf        # Nginx configuration
│   ├── .env.example      # Example environment variables
│   └── .env.prod         # Production environment variables
├── docker-compose.yml    # Docker compose configuration
├── docker-compose-dev.yml # Development Docker compose
├── docker-compose.prod.yml # Production Docker compose
├── devcon                # Development container manager (main tool)
├── dev-docker.sh         # Legacy Docker development script
├── dev.sh                # Direct host development script
├── DEVELOPMENT.md        # Detailed development guide
└── README.md             # Project documentation
```

## Development Approach

**Recommended: Docker Development** - Containerized environment with all dependencies pre-configured:
- ✅ System-upgrade-proof (locked versions)
- ✅ No port conflicts (custom ports: 18529, 41148, 41149)
- ✅ Hot-reload optimized for both backend and frontend
- ✅ One command to start everything
- ✅ Matches production environment

**Alternative: Direct Host Development** - Requires manual installation of uv, bun, and ArangoDB.

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed instructions.

## Quick Start - Docker Development (Recommended)

### Using DevCon - Development Container Manager

The project includes `devcon`, a comprehensive development management script:

```bash
# Core Commands
./devcon up              # Start all services
./devcon down            # Stop all services
./devcon restart         # Restart all services
./devcon status          # Show service status
./devcon logs [service]  # View logs (backend/frontend/db)

# Development Commands
./devcon shell [service] # Open shell (default: backend)
./devcon test            # Run backend tests
./devcon lint            # Run code linting
./devcon format          # Format code with ruff
./devcon build [service] # Rebuild Docker images

# Database Commands
./devcon db-init         # Initialize database with Quran data
./devcon db-reset        # Reset database (warning: deletes data!)
./devcon db-backup       # Backup database
./devcon db-restore      # Restore from backup

# Quick Access
./devcon urls            # Show all service URLs
./devcon ps              # Show running containers
```

### Access Services

- Frontend: <http://localhost:41149> (Vite dev server with hot-reload)
- Backend API: <http://localhost:41148> (FastAPI with auto-reload)
- API Docs: <http://localhost:41148/docs> (Swagger UI)
- ArangoDB: <http://localhost:18529> (Database admin interface)

### Alternative: Direct Host Development

For running services directly on your host (requires uv, bun, and ArangoDB installed):

```bash
./dev.sh all  # Start all services on host
```

Access at standard ports: Frontend (5173), Backend (8000), ArangoDB (8529).

## Daily Development Workflow

### Starting Your Day

```bash
# 1. Start the development environment
./devcon up

# 2. Check all services are running
./devcon status

# 3. Initialize database (first time only)
./devcon db-init
```

### During Development

- **Backend changes**: Edit Python files in `backend/` - auto-reloads
- **Frontend changes**: Edit Vue files in `frontend/src/` - hot-reloads
- **View logs**: `./devcon logs backend` or `./devcon logs frontend`
- **Access backend shell**: `./devcon shell` (for CLI commands)
- **Run tests**: `./devcon test`

### End of Day

```bash
# Stop all services
./devcon down
```

## Backend Development (Python + uv)

This project uses `uv` as the Python package manager for fast, reliable dependency management:

```bash
# Access backend container for development
./dev-docker.sh shell

# Inside container - dependencies are auto-installed
# Run tests with coverage
pytest

# Run linting and formatting
ruff check
ruff format

# CLI management commands
quranref-cli db init                    # Initialize database
quranref-cli db populate-surahs         # Load Surah metadata
quranref-cli db import-text             # Import Quran text
quranref-cli post-process link-ayas-to-surahs  # Create relationships
quranref-cli post-process make-words    # Extract word data
```

### Direct Host Development (Alternative)

```bash
cd backend
uv sync              # Install dependencies from pyproject.toml
uv run fastapi dev quranref/main.py --host 0.0.0.0 --port 8000
```

## Frontend Development (Vue.js + Bun)

Frontend uses Bun for ultra-fast package management and development:

```bash
# Frontend auto-starts with hot-reload when using Docker
# Edit files in frontend/src/ and see changes instantly at http://localhost:41149

# To run commands inside the frontend container:
docker exec quranref_frontend_dev bun run build    # Production build
docker exec quranref_frontend_dev vue-tsc -b       # Type checking
docker exec quranref_frontend_dev bun test         # Run tests
```

### Direct Host Development (Alternative)

```bash
cd frontend
bun install          # Install dependencies
bun run dev          # Start Vite dev server with hot-reload
bun run build        # Create production build
bun run preview      # Preview production build
```

## Production Deployment

The application supports both Docker Swarm and single-node production deployments.

### Prerequisites

**On your local development machine:**

- Docker installed and configured
- Access to production server (SSH, etc.)
- Project source code

**On the production server:**

- Docker installed and configured
- Docker Swarm initialized (for Swarm deployment)
- Environment files configured (copy from `backend/.env` and `frontend/.env`)
- SSL certificates (if using HTTPS)
- Sufficient system resources (CPU, RAM, storage)

### Deployment Steps

#### Method 1: Docker Swarm Deployment (Recommended for production)

**On your local machine:**

1. Build the production images:

```bash
# Build images locally
docker compose -f docker-compose.prod.yml build

# Tag images for your registry (optional)
docker tag quranref_frontend your-registry.com/quranref_frontend:latest
docker tag quranref_backend your-registry.com/quranref_backend:latest

# Push to registry (if using remote registry)
docker push your-registry.com/quranref_frontend:latest
docker push your-registry.com/quranref_backend:latest
```

2. Copy deployment files to production server:

```bash
# Copy necessary files to production server
scp docker-compose.prod.yml user@production-server:/opt/quranref/
scp backend/.env user@production-server:/opt/quranref/backend/
scp frontend/.env user@production-server:/opt/quranref/frontend/
scp -r config/ user@production-server:/opt/quranref/
```

**On the production server:**

```bash
# Initialize Docker Swarm (if not already done)
docker swarm init

# Deploy the stack
cd /opt/quranref
docker stack deploy -c docker-compose.prod.yml quranref

# Check deployment status
docker stack services quranref
docker stack ps quranref
```

#### Method 2: Single-Node Deployment

**On your local machine:**

1. Build and export images:

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Save images to tar files
docker save quranref_frontend:latest | gzip > quranref_frontend.tar.gz
docker save quranref_backend:latest | gzip > quranref_backend.tar.gz

# Transfer to production server
scp *.tar.gz user@production-server:/tmp/
scp docker-compose.prod.yml user@production-server:/opt/quranref/
scp backend/.env user@production-server:/opt/quranref/backend/
scp frontend/.env user@production-server:/opt/quranref/frontend/
scp -r config/ user@production-server:/opt/quranref/
```

**On the production server:**

```bash
# Load images
docker load < /tmp/quranref_frontend.tar.gz
docker load < /tmp/quranref_backend.tar.gz

# Start services
cd /opt/quranref
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs
```

### Post-Deployment Setup

**On the production server:**

```bash
# Initialize database (first-time deployment only)
# For Docker Swarm deployment:
docker exec $(docker ps -q -f name=quranref_backend) quranref-cli db init
docker exec $(docker ps -q -f name=quranref_backend) quranref-cli db populate-surahs
docker exec $(docker ps -q -f name=quranref_backend) quranref-cli db import-text
docker exec $(docker ps -q -f name=quranref_backend) quranref-cli post-process link-ayas-to-surahs
docker exec $(docker ps -q -f name=quranref_backend) quranref-cli post-process make-words

# For single-node deployment:
docker exec quranref-backend-1 quranref-cli db init
docker exec quranref-backend-1 quranref-cli db populate-surahs
docker exec quranref-backend-1 quranref-cli db import-text
docker exec quranref-backend-1 quranref-cli post-process link-ayas-to-surahs
docker exec quranref-backend-1 quranref-cli post-process make-words
```

### Production Services Access

- Frontend: <http://your-server-ip> (port 80)
- Backend API: <http://your-server-ip:8000>
- ArangoDB: <http://your-server-ip:8529> (admin interface - secure this!)

### Data Persistence

Production data is stored in Docker volumes:

- `quranref_data`: ArangoDB data volume

### Monitoring and Maintenance

**On the production server:**

```bash
# View logs
docker stack ps quranref  # For Swarm
docker compose -f docker-compose.prod.yml logs  # For single-node

# Update deployment
docker stack deploy -c docker-compose.prod.yml quranref  # For Swarm
docker compose -f docker-compose.prod.yml up -d  # For single-node

# Backup database
# For Docker Swarm:
docker exec $(docker ps -q -f name=quranref_backend) arangodump --server.endpoint tcp://db:8529 --output-directory /backup
# For single-node:
docker exec quranref-backend-1 arangodump --server.endpoint tcp://db:8529 --output-directory /backup
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
