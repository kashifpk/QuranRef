# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QuranRef is a web application providing searchable access to the Holy Quran and its translations. It has a FastAPI backend and a Vue.js 3 frontend. The Quran text is stored as a graph in Apache AGE (a PostgreSQL extension); users, bookmarks and metadata are ordinary PostgreSQL tables.

## Development Commands

Development runs directly on the host. There is no container requirement. The local database is PostgreSQL 18 with AGE 1.8.0 on port 5433 (the 16 cluster on 5432 belongs to other projects); production is PostgreSQL 16 with AGE 1.6.0 and CI runs the tests against both.

`direnv` loads `.env.dev` (database connection, `ENVIRONMENT=development`). Google OAuth credentials go in `backend/.env` (gitignored), never in `.env.dev`: direnv would export empty values that override `backend/.env`.

### Backend (run from backend/)

```bash
uv sync --all-extras                 # age-orm is an editable path dependency (see pyproject.toml)
python -m quranref                   # dev server on http://localhost:41148 with auto-reload
uv run pytest                        # creates and drops quranref_test on the host PostgreSQL
uv run ruff check quranref tests
uv run ruff format quranref tests
uv run bandit -q -r quranref
```

CLI, run as `uv run quranref-cli <group> <command>`:

- `db init`: create graph, labels, indexes, then run Alembic migrations
- `db migrate`: Alembic upgrade head only
- `db populate-surahs`: load Surah metadata
- `db import-text <language> <text_name> <file>`: import Arabic text or a translation
- `db import-json <dir>` and `db export-json`: bulk graph import and export (used for migrations)
- `post-process link-ayas-to-surahs`, `make-words`, `update-meta-info`, `fix-word-counts`, `remove-bismillah`

### Frontend (run from frontend/)

```bash
bun install
bun run dev                          # http://localhost:41149, Vite proxies /api to the backend
bun run vue-tsc -b                   # type check
bun run build                        # type check, then production build into ../static
```

Always use bun, never npm, npx or node. After changing package.json run `bun install`.

Ports are hardcoded: backend 41148 in `__main__.py`, frontend 41149 in `vite.config.ts`.

`./devhost start|stop|status|logs` runs both dev servers detached; runtime files land in `.claude-work/`.

### Container alternative (optional)

`./devcon up` starts PostgreSQL + AGE (host port 15432, override with `DEV_DB_PORT` when that port is taken, as it is on the main dev machine), the backend and the frontend in containers through docker compose (Podman preferred, Docker fallback). `AGE_IMAGE_TAG=release_PG18_1.8.0 ./devcon up` runs PostgreSQL 18 instead. Run `./devcon sync` after dependency changes and `./devcon build` after Dockerfile changes. The age-orm source is mounted at `/age-orm` in the backend container.

### CI

`.github/workflows/ci.yml` runs ruff check, ruff format check and pytest against an `apache/age` service container, and vue-tsc plus the Vite build for the frontend.

## Architecture Overview

### Backend (FastAPI + Apache AGE)

- Framework: FastAPI
- Graph database: Apache AGE via age-orm. Graph `quran_graph` with vertex labels `Surah`, `Aya`, `Text`, `Word` and edge labels `HAS_AYA`, `HAS_WORD`, `AYA_TEXT`
- Relational tables: SQLAlchemy 2 models with Alembic migrations (`users`, `meta_info`, `bookmarks`)
- API: REST endpoints under `/api/v1`
- CLI: Typer (`quranref-cli`)
- Configuration: pydantic-settings, environment variables first, then `backend/.env`

Key files:

- `backend/quranref/main.py`: application entry point, CORS, session middleware, SPA static serving
- `backend/quranref/api.py`: Quran text, search and word endpoints
- `backend/quranref/auth.py`: Google OAuth and JWT auth endpoints
- `backend/quranref/auth_utils.py`: JWT create and verify helpers
- `backend/quranref/dependencies.py`: auth dependencies for protected endpoints
- `backend/quranref/bookmarks.py`: bookmarks endpoints
- `backend/quranref/models.py`: age-orm graph models
- `backend/quranref/sql_models.py`: SQLAlchemy models
- `backend/quranref/schemas.py`: Pydantic request and response models
- `backend/quranref/db.py`: age-orm database, graph factory, SQLAlchemy engine and session
- `backend/quranref/settings.py`: settings
- `backend/quranref/cli.py` and `commands/`: management CLI
- `backend/alembic/`: migrations (0001 users and meta_info, 0002 bookmarks)

### Frontend (Vue.js 3 + TypeScript)

- Vue 3 Composition API with `<script setup>` and TypeScript strict mode
- PrimeVue 4 with the Aura theme (green preset in `plugins/primevue.ts`)
- Pinia store (`store.ts`), Vue Router (`router.ts`), VueUse, mande and fetch for HTTP
- Dark and light mode, responsive layout

Key files: `frontend/src/main.ts`, `QuranRefMainApp.vue`, `store.ts`, `router.ts`, `type_defs.ts`, `components/`, `views/`.

### Database Design

- Graph: Surah -[HAS_AYA]-> Aya -[HAS_WORD]-> Word, Aya -[AYA_TEXT]-> Text
- Text vertices are deduplicated by SHA-256 hash stored as `id`
- Arabic text variants and translations are AYA_TEXT edges with `language` and `text_type` properties
- Unique indexes on vertex `id` fields; indexes on `word`, `count`, `surah_key`
- `meta_info`, `users`, `bookmarks` are ordinary PostgreSQL tables managed by Alembic

### Authentication

- Google OAuth 2.0 authorization code flow via authlib
- JWT in an httpOnly cookie (`access_token`), 30 day expiry by default
- All Quran endpoints are public. `get_current_user` (optional) and `require_current_user` (401) in `dependencies.py` protect user-specific endpoints such as bookmarks
- Endpoints: `/api/v1/auth/login`, `callback`, `me`, `logout`
- Production credentials are deployed by the Ansible template `env.production.j2` from the vault

## Development Conventions

### Python (backend)

- Python 3.12+ with modern type hints; uv for dependencies (not Poetry)
- ruff for lint and format, line length 100. Run both before committing
- Route handlers that use age-orm or SQLAlchemy are plain `def`. Both drivers are synchronous and FastAPI runs sync handlers in a thread pool. Use `async def` only when the handler awaits something
- Prefer Pydantic models over raw dictionaries
- pytest with fixtures, 50% minimum coverage, `QURANREF_TESTING=true` and `ENVIRONMENT=testing` set by pytest-env
- PEP 257 docstrings

### TypeScript and Vue (frontend)

- Composition API with `<script setup>`
- VueUse for reactivity helpers
- PrimeVue 4 components for UI consistency
- Mobile-first responsive design
- Pinia for state

### General

- Check for similar existing files before creating new ones
- Follow existing patterns and naming
- Use the CLI for database operations
- Temporary scripts go in `.claude-work/` (gitignored)

## Environment Configuration

`.env.dev` (loaded by direnv on the host):

```bash
DB_HOST=localhost
DB_PORT=5433
DB_NAME=quranref
DB_USERNAME=<pg user>
DB_PASSWORD=<pg password>
ENVIRONMENT=development
DEBUG=true
JWT_SECRET_KEY=<32+ bytes>
FRONTEND_URL=http://localhost:41149
```

`docker-compose.dev.yml` sets `DB_HOST=postgres` and the other variables for containers. The test fixtures read the database connection from environment variables first, then `.env.dev`.

## Testing and Quality

- Backend: pytest with fixtures and type annotations, pytest-mock for mocking, minimum 50% coverage. Tests need a reachable PostgreSQL with AGE; they create and drop `quranref_test`
- Frontend: `vue-tsc -b` for type checking
- Security: `bandit -q -r quranref`
- Run ruff, pytest and vue-tsc before committing

## Data Management

1. Init: `db init` creates the graph, labels, indexes and runs migrations
2. Import: `db import-text` per text, or `db import-json` from an export
3. Link: `post-process link-ayas-to-surahs`
4. Words: `post-process make-words`
5. Meta: `post-process update-meta-info`

## API Usage

Base URL in development: http://localhost:41148/api/v1. Interactive docs at /docs.

- `GET /surahs`
- `GET /text/{ayas_spec}/{languages_spec}`
- `GET /search/{term}/{search_lang}/{translation_langs}`
- `GET /words-by-letter/{letter}`, `GET /ayas-by-word/{word}/{languages}`
- `GET /words-by-count/{count}`, `GET /available-word-counts`, `GET /top-most-frequent-words/{limit}`
- `GET /text-types`, `GET /letters`
- `GET /auth/login`, `GET /auth/callback`, `GET /auth/me`, `POST /auth/logout`
- `GET /bookmarks`, `GET|PUT|DELETE /bookmarks/reading`, `POST /bookmarks/notes`, `PUT|DELETE /bookmarks/notes/{id}`

## Deployment

Production runs on a VPS with systemd and Caddy (no containers). Deployment uses Ansible:

```bash
cd frontend && bun run build && cd ..
cd deploy && ansible-playbook playbooks/deploy.yml -i inventory.yml
ssh kashif@hosting_vps "cd /home/kashif/QuranRef/backend && .venv/bin/quranref-cli db init"   # after schema changes
```

Key files:

- `deploy/playbooks/deploy.yml`: routine deployment (sync code, deploy .env, install deps, restart)
- `deploy/playbooks/setup.yml`: first-time setup (AGE build, database, app)
- `deploy/roles/app_deploy/templates/env.production.j2`: production environment template
- `deploy/group_vars/all/vars.yml`: variables; secrets reference the vault
- `deploy/group_vars/all/vault.yml`: secrets (gitignored, encrypt with `ansible-vault`)

Production URLs: https://quranref.info and https://quranref.info/api/v1.

## Third-party licensing

PrimeVue 5 and PrimeIcons 8 moved to the PrimeUI license, which is not open source. Keep PrimeVue, @primevue/themes and PrimeIcons on their MIT majors (4.x, 4.x, 7.x) unless there is an explicit licensing decision.
