# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuranRef is a modern web application providing searchable access to the Holy Quran and its translations. It uses a **client-server architecture** with a FastAPI backend and Vue.js frontend, leveraging Apache AGE (PostgreSQL graph extension) for complex Islamic text relationships.

## Development Commands

### Quick Start - Docker Development

**Single unified development approach using custom ports to avoid conflicts:**

```bash
# Start all services in containers (system-upgrade-proof)
./devcon up       # Start all services
./devcon logs     # View logs from all services
./devcon down     # Stop all services
./devcon build    # Rebuild after Dockerfile changes
./devcon sync     # Sync dependencies after package.json/pyproject.toml changes
```

**Important: After changing dependencies** (package.json or pyproject.toml), run `./devcon sync` to install new packages in containers. The container uses anonymous volumes for node_modules/venv, so rebuilding alone won't update them.

**Access your application:**
- Frontend: http://localhost:41149 (Vite dev server)
- Backend API: http://localhost:41148 (FastAPI)
- PostgreSQL: localhost:15432 (Database)

### Backend Development (Inside Container)

```bash
# Access backend container shell
./devcon shell

# Inside container:
# Run tests with coverage
pytest

# Run linting and formatting
ruff check
ruff format

# CLI management commands (database operations)
quranref-cli db init                    # Initialize graph, labels, indexes, meta_info table
quranref-cli db populate-surahs         # Load Surah metadata
quranref-cli db import-text             # Import Arabic text and translations from text files
quranref-cli db import-json <data-dir>  # Bulk import from JSON exports (migration)
quranref-cli post-process link-ayas-to-surahs  # Create HAS_AYA graph relationships
quranref-cli post-process make-words    # Extract and count words
quranref-cli post-process update-meta-info     # Populate text-types metadata
quranref-cli post-process fix-word-counts      # Recalculate word counts from edges
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
./devcon shell   # Access backend container shell
./devcon clean   # Clean up all resources
./devcon backend # Show backend logs only
./devcon frontend # Show frontend logs only
./devcon db      # Show database logs only
```

### Local Development (without Docker)

```bash
# Backend (from backend/ directory) — runs on port 41148
python -m quranref

# Frontend (from frontend/ directory) — runs on port 41149
bun run dev

# Run backend tests
uv run pytest
```

Ports are hardcoded: backend `41148` in `__main__.py`, frontend `41149` in `vite.config.ts`. The Vite dev server proxies `/api/*` to the backend.

Environment: `direnv` loads `.env.dev` automatically. Google OAuth credentials go in `backend/.env` (gitignored) — do NOT put them in `.env.dev` as direnv would export empty values that override `backend/.env`.

### Why Docker-Only Development?

**Benefits of this approach:**
- System-Upgrade-Proof: Locked Docker images prevent version drift
- Port Conflict-Free: Custom ports (15432, 41148, 41149) avoid conflicts
- Production Parity: Mirrors Docker Swarm production environment
- Team Consistency: Works identically across all developer machines
- Excellent Hot-Reload: Optimized volume mounts for FastAPI and Vite
- Simple Onboarding: One command starts everything

## Architecture Overview

### Backend (FastAPI + Apache AGE)
- **Framework**: FastAPI with async/await patterns
- **Database**: Apache AGE (PostgreSQL graph extension) via age-orm
- **Graph**: `quran_graph` with vertex labels: `Surah`, `Aya`, `Text`, `Word` and edge labels: `HAS_AYA`, `HAS_WORD`, `AYA_TEXT`
- **MetaInfo**: Regular PostgreSQL table (`meta_info`) for key-value metadata
- **Models**: age-orm Vertex/Edge models (`models.py`)
- **API**: REST endpoints at `/api/v1/` for Quran data and search
- **CLI**: Typer-based management tools (`quranref-cli`)
- **Configuration**: Pydantic settings with environment-based config

Key files:
- `backend/quranref/main.py`: Application entry point
- `backend/quranref/api.py`: REST API endpoints
- `backend/quranref/auth.py`: Google OAuth + JWT auth endpoints
- `backend/quranref/auth_utils.py`: JWT create/verify helpers
- `backend/quranref/dependencies.py`: Auth dependencies for protected endpoints
- `backend/quranref/models.py`: AGE graph vertex/edge models
- `backend/quranref/db.py`: Database connection and graph factory
- `backend/quranref/cli.py`: Management CLI commands

### Frontend (Vue.js 3 + TypeScript)
- **Framework**: Vue.js 3 with Composition API and TypeScript
- **UI Library**: PrimeVue 4 with Aura theme (green palette)
- **State Management**: Pinia store (`store.ts`)
- **Routing**: Vue Router 4 with history mode
- **Build Tool**: Vite with custom mounting system
- **HTTP Client**: Mande for API communication
- **Features**: Dark/light mode toggle, responsive design

Key files:
- `frontend/src/QuranRefMainApp.vue`: Main application shell
- `frontend/src/store.ts`: Pinia store for global state
- `frontend/src/router.ts`: Route definitions
- `frontend/src/type_defs.ts`: TypeScript interfaces

### Database Design
- **Graph Structure**: Surah -[HAS_AYA]-> Aya -[HAS_WORD]-> Word, Aya -[AYA_TEXT]-> Text
- **Text Storage**: Deduplicated using SHA-256 hashes (stored as `id` property)
- **Multi-language**: Arabic text variants + 100+ translations via AYA_TEXT edge properties
- **Indexing**: Unique indexes on vertex `id` fields, indexes on `word`, `count`, `surah_key`
- **MetaInfo**: Regular PostgreSQL table for key-value store (not a graph vertex)
- **Users**: Regular PostgreSQL table for Google OAuth user accounts

### Authentication
- **Google OAuth 2.0** server-side authorization code flow via authlib
- **JWT tokens** stored in httpOnly cookies (72h expiry)
- All existing endpoints remain **public** — auth is optional
- `get_current_user` (optional) and `require_current_user` (strict 401) dependencies in `dependencies.py` for future protected endpoints
- Auth endpoints at `/api/v1/auth/`: `login`, `callback`, `me`, `logout`
- Google OAuth credentials stored in `backend/.env` (gitignored), not in `.env.dev`
- Production credentials deployed via Ansible template (`env.production.j2`)

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
- Use **PrimeVue 4 components** for UI consistency (Aura theme)
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
# Database credentials (PostgreSQL + Apache AGE)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=quranref
DB_USERNAME=quranref
DB_PASSWORD=compulife

# Application settings
ENVIRONMENT=development
DEBUG=true
```

**Container networking automatically handles:**
- Backend connects to database via `postgres:5432` (internal)
- Frontend connects to backend via `http://localhost:41148` (external)
- All services accessible on host via custom ports (15432, 41148, 41149)

**age-orm development**: The age-orm source is mounted at `/age-orm` in the backend container for editable install. Production builds install from PyPI.

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

1. **Init**: Create graph, vertex/edge labels, indexes, and meta_info table
2. **Import**: JSON bulk import (migration) or text file import
3. **Link**: Create Surah-Aya graph relationships (HAS_AYA edges)
4. **Process**: Extract words with frequency counts (Word vertices + HAS_WORD edges)
5. **Meta**: Update text-types metadata in meta_info table

Use `quranref-cli` commands for all data operations to maintain consistency.

## API Usage

Key API endpoints for development (available at http://localhost:41148):
- `GET /api/v1/surahs` - All Surah metadata
- `GET /api/v1/text/{surah_number}/{text_types}` - Surah text with translations
- `GET /api/v1/search/{term}/{search_lang}/{translation_langs}` - Search functionality
- `GET /api/v1/words-by-letter/{letter}` - Word browsing
- `GET /api/v1/ayas-by-word/{word}/{languages}` - Verse lookup by word

Auth endpoints:
- `GET /api/v1/auth/login` - Redirect to Google OAuth
- `GET /api/v1/auth/callback` - Google OAuth callback (sets JWT cookie)
- `GET /api/v1/auth/me` - Current user info or `{"user": null}`
- `POST /api/v1/auth/logout` - Clear auth cookie

The frontend uses these endpoints through the Pinia store and component-level API calls.

## Deployment

Production runs on a VPS with **systemd + Caddy** (not Docker). Deployment uses **Ansible**:

```bash
# Build frontend first
cd frontend && bun run build && cd ..

# Deploy via Ansible (syncs code, deploys .env, installs deps, restarts service)
cd deploy && ansible-playbook playbooks/deploy.yml -i inventory.yml

# If database schema changed (e.g., new tables), run on production:
ssh kashif@hosting_vps "cd /home/kashif/QuranRef/backend && .venv/bin/quranref-cli db init"
```

Key deployment files:
- `deploy/playbooks/deploy.yml`: Main deployment playbook
- `deploy/roles/app_deploy/templates/env.production.j2`: Production environment template
- `deploy/group_vars/all.yml`: Ansible variables (secrets reference vault)
- `deploy/group_vars/vault.yml`: Encrypted secrets (gitignored, encrypt with `ansible-vault`)

Production URLs:
- Frontend: https://quranref.info
- API: https://quranref.info/api/v1
