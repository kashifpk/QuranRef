# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuranRef is a modern web application providing searchable access to the Holy Quran and its translations. It uses a **client-server architecture** with a FastAPI backend and Vue.js frontend, leveraging ArangoDB's graph database capabilities for complex Islamic text relationships.

## Development Commands

### Quick Start - Docker Development

**Single unified development approach using custom ports to avoid conflicts:**

```bash
# Start all services in containers (system-upgrade-proof)
./dev-docker.sh up      # Start all services
./dev-docker.sh logs    # View logs from all services  
./dev-docker.sh down    # Stop all services
./dev-docker.sh build   # Rebuild after dependency changes
```

**Access your application:**
- Frontend: http://localhost:41149 (Vite dev server)
- Backend API: http://localhost:41148 (FastAPI)
- ArangoDB: http://localhost:18529 (Database admin)

**Data Migration (if upgrading from Podman):**
```bash
# Check if you have existing Podman data
./migrate-podman-to-docker.sh check

# Migrate existing data from Podman to Docker
./migrate-podman-to-docker.sh migrate
```

### Backend Development (Inside Container)

```bash
# Access backend container shell
./dev-docker.sh shell

# Inside container:
# Run tests with coverage
pytest

# Run linting and formatting
ruff check
ruff format

# CLI management commands (database operations)
quranref-cli db init                    # Initialize database structure
quranref-cli db populate-surahs         # Load Surah metadata
quranref-cli db import-text             # Import Arabic text and translations
quranref-cli post-process link-ayas-to-surahs  # Create graph relationships
quranref-cli post-process make-words    # Extract and count words
```

### Frontend Development (Automatic)

```bash
# Frontend development happens automatically with hot-reload
# Edit files in frontend/src/ and see changes instantly at http://localhost:41149

# To build for production (inside container):
docker exec quranref_frontend_dev bun run build

# To run type checking (inside container):
docker exec quranref_frontend_dev vue-tsc -b
```

### Additional Docker Commands

```bash
# Advanced Docker development commands
./dev-docker.sh shell   # Access backend container shell
./dev-docker.sh clean   # Clean up all resources
./dev-docker.sh backend # Show backend logs only
./dev-docker.sh frontend # Show frontend logs only
./dev-docker.sh db      # Show database logs only
```

### Why Docker-Only Development?

**Benefits of this approach:**
- ✅ **System-Upgrade-Proof**: Locked Docker images prevent version drift
- ✅ **Port Conflict-Free**: Custom ports (18529, 41148, 41149) avoid conflicts
- ✅ **Production Parity**: Mirrors Docker Swarm production environment
- ✅ **Team Consistency**: Works identically across all developer machines
- ✅ **Excellent Hot-Reload**: Optimized volume mounts for FastAPI and Vite
- ✅ **Simple Onboarding**: One command starts everything

## Architecture Overview

### Backend (FastAPI + ArangoDB)
- **Framework**: FastAPI with async/await patterns
- **Database**: ArangoDB graph database with collections: `surahs`, `ayas`, `texts`, `words`, `meta_info`
- **Models**: ArangoDB documents using arango-orm (`models.py`)
- **API**: REST endpoints at `/api/v1/` for Quran data and search
- **CLI**: Typer-based management tools (`quranref-cli`)
- **Configuration**: Pydantic settings with environment-based config

Key files:
- `backend/quranref/main.py`: Application entry point
- `backend/quranref/api.py`: REST API endpoints
- `backend/quranref/models.py`: ArangoDB document models
- `backend/quranref/cli.py`: Management CLI commands

### Frontend (Vue.js 3 + TypeScript)
- **Framework**: Vue.js 3 with Composition API and TypeScript
- **UI Library**: Vuetify (Material Design)
- **State Management**: Pinia store (`store.ts`)
- **Routing**: Vue Router 4 with history mode
- **Build Tool**: Vite with custom mounting system
- **HTTP Client**: Mande for API communication

Key files:
- `frontend/src/QuranRefMainApp.vue`: Main application shell
- `frontend/src/store.ts`: Pinia store for global state
- `frontend/src/router.ts`: Route definitions
- `frontend/src/type_defs.ts`: TypeScript interfaces

### Database Design
- **Graph Structure**: Surahs → Ayas → Words with `has` relationships
- **Text Storage**: Deduplicated using SHA-256 hashes
- **Multi-language**: Arabic text variants + 100+ translations
- **Indexing**: Strategic indexes on `word`, `count`, and hash fields

## Development Conventions

### Python (Backend)
- Use **Python 3.12+** with modern type hints
- Use **uv** package manager instead of Poetry
- Follow **ruff** formatting and linting rules (line length: 100)
- Use **async/await** for FastAPI endpoints
- Prefer **Pydantic models** over raw dictionaries
- Use **pytest** with fixtures for testing (50% coverage minimum)
- Document functions with **PEP 257** docstrings

### TypeScript/Vue (Frontend)
- Use **Vue 3 Composition API** with `<script setup>` syntax
- Leverage **VueUse** functions for reactivity
- Follow **TypeScript strict mode** with proper type annotations
- Use **Vuetify components** for UI consistency
- Implement **responsive design** with mobile-first approach
- Use **Pinia** for state management

### General Guidelines
- Always check if similar files exist before creating new ones
- Use **uv** for Python dependency management (not Poetry)
- Follow existing code patterns and naming conventions
- Maintain separation between frontend/backend environments
- Use provided CLI tools for database operations

## Environment Configuration

### Docker Development Environment

The Docker setup uses `.env.dev` for container-specific environment variables:

```bash
# Database credentials
ARANGO_ROOT_PASSWORD=Test123!
DB_NAME=quranref
DB_USERNAME=quranref
DB_PASSWORD=compulife

# Application settings
ENVIRONMENT=development
DEBUG=true
```

**Container networking automatically handles:**
- Backend connects to database via `http://arangodb:8529` (internal)
- Frontend connects to backend via `http://localhost:41148` (external)
- All services accessible on host via custom ports (18529, 41148, 41149)

## Testing and Quality

### Backend Testing
- Use **pytest** with fixtures pattern
- Include type annotations in all tests
- Use **pytest-mock** for mocking
- Maintain minimum 50% code coverage
- Test environment: `QURANREF_TESTING=true`

### Code Quality
- **Backend**: Use `ruff` for linting and formatting
- **Frontend**: Use `vue-tsc` for type checking
- **Security**: Use `bandit` for security analysis
- Run quality checks before committing changes

## Data Management

The application manages Quranic text through a structured pipeline:

1. **Import**: Raw text files → ArangoDB collections
2. **Link**: Create Surah-Aya graph relationships  
3. **Process**: Extract words with frequency counts
4. **Index**: Update search indexes and metadata

Use `quranref-cli` commands for all data operations to maintain consistency.

## API Usage

Key API endpoints for development (available at http://localhost:41148):
- `GET /api/v1/surahs` - All Surah metadata
- `GET /api/v1/text/{surah_number}/{text_types}` - Surah text with translations
- `GET /api/v1/search/{term}/{search_lang}/{translation_langs}` - Search functionality
- `GET /api/v1/words-by-letter/{letter}` - Word browsing
- `GET /api/v1/ayas-by-word/{word}/{languages}` - Verse lookup by word

The frontend uses these endpoints through the Pinia store and component-level API calls.

## Deployment

**For deployment tasks, use the specialized deployment agent:**

The project includes a deployment agent configuration in `.claude-agents/` that handles:
- Building and tagging Docker images
- Pushing to production registry
- Deploying to Docker Swarm
- Monitoring deployment status
- Handling rollbacks

To deploy, simply ask: "Deploy the frontend to production" or "Deploy to swarm"

The agent knows about:
- Docker contexts (production via SSH)
- Registry configuration (localhost:5000)
- Service names and URLs
- Common deployment issues and solutions
- Emergency procedures

See `.claude-agents/deploy-agent.md` for detailed deployment procedures.