# Quran Reference

Online, searchable reference of the Holy Quran and its translations. Live at https://quranref.info.

## Stack

- Backend: Python 3.12+, FastAPI, Apache AGE (PostgreSQL graph extension) through age-orm, SQLAlchemy and Alembic for relational tables, Typer CLI. Dependencies managed with uv.
- Frontend: Vue 3 with TypeScript, PrimeVue 4 (Aura theme), Pinia, Vue Router, Vite. Dependencies managed with Bun.
- Database: PostgreSQL with Apache AGE. Production runs PostgreSQL 16 with AGE 1.6.0; local development runs PostgreSQL 18 with AGE 1.8.0, and CI tests both. Graph `quran_graph` holds the Quran text; users, bookmarks and metadata live in ordinary tables.
- Production: a single VPS running systemd and Caddy, deployed with Ansible.

## Layout

```text
backend/                FastAPI app (quranref/), tests/, alembic/, data files (data/), pyproject.toml
frontend/               Vue app (src/), vite.config.ts, package.json
deploy/                 Ansible playbooks, roles and inventory
static/                 Frontend build output (gitignored), served by the backend in production
.env.dev                Local development environment variables, loaded by direnv
devcon                  Optional container-based development environment
docker-compose.dev.yml  Compose file used by devcon
.github/workflows/      CI (ruff, pytest, vue-tsc, vite build)
```

## Local development

Requirements: PostgreSQL 18 with the Apache AGE 1.8.0 extension, uv, bun, direnv. (Production is still on PostgreSQL 16 with AGE 1.6.0; the code works on both.)

On Ubuntu 24.04, PostgreSQL 18 comes from the PGDG apt repository (`/usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y`, then `apt install postgresql-18 postgresql-server-dev-18`); Ubuntu 26.04 ships it natively. AGE is built from source: download the `PG18/v1.8.0-rc0` tarball from the apache/age releases, run `make` and `make install` with `PG_CONFIG=/usr/lib/postgresql/18/bin/pg_config`, and set `shared_preload_libraries = 'age'` for the cluster. The Ansible role in `deploy/roles/age_install` does the same for the server. The local 18 cluster listens on port 5433 so it can coexist with a 16 cluster on 5432.

1. Environment. Run `direnv allow` once. It loads `.env.dev` (database host, user, password, `ENVIRONMENT=development`). Google OAuth credentials go in `backend/.env` (gitignored), never in `.env.dev`, because direnv would export empty values that override `backend/.env`.
2. Database. Create a database named as in `.env.dev`, owned by that user, and run `CREATE EXTENSION age;` in it. The user needs the superuser attribute (AGE requires it for `LOAD`).
3. Backend:

   ```bash
   cd backend
   uv sync --all-extras
   uv run quranref-cli db init             # graph, labels, indexes, Alembic migrations
   uv run quranref-cli db populate-surahs
   python -m quranref                      # http://localhost:41148, auto-reload
   ```

4. Frontend:

   ```bash
   cd frontend
   bun install
   bun run dev                             # http://localhost:41149, /api proxied to the backend
   ```

Ports are fixed: backend 41148 in `backend/quranref/__main__.py`, frontend 41149 in `frontend/vite.config.ts`.

`./devhost start` runs both servers detached from the terminal (`stop`, `status`, `logs`); pids and logs go to the gitignored `.claude-work/` directory.

### Loading the Quran text

Text files live in `backend/data`. Run from `backend/` with `uv run quranref-cli ...`:

```bash
db import-text arabic simple data/quran-simple.txt.bz2   # language, text name, file
db import-text <language> <translator> data/translations/<file>
post-process link-ayas-to-surahs
post-process make-words
post-process update-meta-info
post-process build-search-index          # rebuild the normalized search table after any text change
```

`db import-json <dir>` and `db export-json` move the whole graph in and out as JSON, which is the way to migrate between PostgreSQL or AGE versions. `post-process fix-word-counts` recalculates word counts from edges.

### Word morphology (roots, lemmas, word-by-word)

The word layer comes from the Quranic Arabic Corpus morphology (GPL, see `backend/data/morphology/NOTICE.md`). It adds Root, Lemma and Token vertices to the graph, aligned to the simple-clean words, and powers the word-by-word reading mode, the lemma and root pages and browse by root.

```bash
db import-morphology data/morphology/quran-morphology.txt   # after make-words
db import-word-glosses english data/qul/english-wbw-translation.json     # per-word meanings
db import-word-glosses urdu data/qul/urud-wbw.json
db import-word-glosses transliteration data/qul/english-wbw-transliteration.json
```

Word-by-word meaning files are not bundled (`backend/data/qul/` is gitignored). QUL (https://qul.tarteel.ai/resources) publishes English (translation resource 92) and Urdu (93) word-by-word translations and an English word-by-word transliteration (transliteration resource 71) as JSON, downloadable with a free account; the importer reads their `{"surah:aya:word": "text"}` format. Meanings are stored per occurrence, so a lemma's page shows which meanings it takes across the Quran. On AGE 1.8 the import is a single SQL update (about 35 seconds for the whole Quran); on AGE 1.6 it falls back to one Cypher update per word.

Search runs on the `aya_search` table, a normalized copy of every aya text with a trigram index (`pg_trgm`), so queries are diacritic, case and letter-variant insensitive. Rebuild it with `post-process build-search-index` whenever texts are imported or changed.

### Tests and quality

```bash
cd backend
uv run pytest                        # creates and drops quranref_test on the configured server
uv run ruff check quranref tests
uv run ruff format quranref tests
cd ../frontend
bun run test                         # Vitest unit and component tests (src/**/*.spec.ts)
bun run vue-tsc -b                   # type check
bun run build                        # type check, then production build into ../static
```

CI runs the same checks on GitHub Actions.

## Container-based development (optional)

`devcon` wraps docker compose (Podman preferred, Docker as fallback) with a PostgreSQL + AGE container on host port 15432 (override with `DEV_DB_PORT` if that port is taken) and hot-reloading backend and frontend containers on the usual 41148 and 41149 ports. It is handy for trying another PostgreSQL or AGE version without touching the host installation.

```bash
./devcon up                                     # PostgreSQL 16 + AGE 1.6.0, matching production
AGE_IMAGE_TAG=release_PG18_1.8.0 ./devcon up    # PostgreSQL 18 + AGE 1.8.0
DEV_DB_PORT=15436 ./devcon up                   # different host port for the database
./devcon shell | logs | test | down
./devcon sync                                   # after dependency changes
./devcon build                                  # after Dockerfile changes
```

If the age-orm source is present at `/MyWork/Projects/age-forge/age-orm`, it is mounted at `/age-orm` in the backend container and installed in editable mode on start.

## Deployment

```bash
cd frontend && bun run build && cd ..
cd deploy && ansible-playbook playbooks/deploy.yml -i inventory.yml
```

`playbooks/setup.yml` does the first-time server setup (AGE build, database, app). Secrets are in `deploy/group_vars/all/vault.yml`, which is gitignored and should be encrypted with `ansible-vault`. After schema changes run `quranref-cli db init` on the server.

## Third-party licensing

PrimeVue 5 and PrimeIcons 8 are distributed under the PrimeUI license, which is not open source. This project pins PrimeVue 4.x, @primevue/themes 4.x and PrimeIcons 7.x, which remain MIT.
