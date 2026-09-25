# QuranRef Backend

FastAPI service exposing the Quran text, translations, word index and search, plus Google OAuth login and per-user bookmarks.

## Stack

- FastAPI with Pydantic settings
- Apache AGE (PostgreSQL graph extension) through age-orm. Graph `quran_graph` with vertex labels Surah, Aya, Text, Word and edge labels HAS_AYA, HAS_WORD, AYA_TEXT
- SQLAlchemy 2 and Alembic for the relational tables (users, meta_info, bookmarks)
- Typer CLI (`quranref-cli`) for database setup and data import
- uv for dependencies, ruff for lint and format, pytest for tests

## Modules

- `main.py`: app setup, CORS, session middleware, SPA static file serving in production
- `api.py`: Quran text, search and word endpoints
- `auth.py`, `auth_utils.py`, `dependencies.py`: Google OAuth, JWT cookies, auth dependencies
- `bookmarks.py`: reading position and note bookmarks
- `words.py`: word morphology endpoints; `morphology.py` parses and aligns the corpus data; `glosses.py` imports per-word meanings
- `topics.py`, `related.py`: topics, themes, similar ayas and recurring phrases; `commands/qul.py` imports them from QUL files
- `textnorm.py`, `search_index.py`: search normalization and the aya_search table builder
- `models.py`: age-orm graph models
- `sql_models.py`: SQLAlchemy models
- `schemas.py`: Pydantic request and response models
- `db.py`: age-orm database and SQLAlchemy engine/session helpers
- `settings.py`: configuration
- `cli.py`, `commands/`: management commands

## Running

See the root README for the full local setup. From this directory:

```bash
uv sync --all-extras              # age-orm is an editable path dependency, see pyproject.toml
python -m quranref                # http://localhost:41148 with auto-reload
uv run pytest                     # creates and drops quranref_test on the configured server
uv run ruff check quranref tests
uv run ruff format quranref tests
```

Route handlers that use age-orm or SQLAlchemy are plain `def` functions. Both drivers are synchronous, and FastAPI runs sync handlers in a thread pool. Use `async def` only for handlers that actually await something.

## Configuration

Settings are read from environment variables first, then from `backend/.env` (gitignored). Field names map to variables case-insensitively.

Required: `ENVIRONMENT`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`.
Optional: `DB_HOST` (localhost), `DB_PORT` (5432), `DEBUG`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY` (at least 32 bytes), `JWT_EXPIRY_HOURS` (720), `FRONTEND_URL`, `BACKEND_URL`, `STATIC_DIR`.

## API

All endpoints are under `/api/v1`. Interactive docs at `/docs`.

- `GET /surahs`
- `GET /text/{ayas_spec}/{languages_spec}` (for example `2:1-5/arabic:simple_english:maududi`)
- `GET /search/{term}/{search_lang}/{translation_langs}`
- `GET /words-by-letter/{letter}`, `GET /ayas-by-word/{word}/{languages}`
- `GET /words-by-count/{count}`, `GET /available-word-counts`, `GET /top-most-frequent-words/{limit}`
- `GET /text-types`, `GET /letters`
- `GET /aya-words/{aya_key}`, `GET /lemma/{lemma}?text_type=simple`, `GET /root/{root}`, `GET /roots-by-letter/{letter}`, `GET /word-morphology/{word}`
- `GET /topics`, `GET /topic/{id}`, `GET /topic/{id}/ayas`, `GET /aya-topics/{aya_key}`, `GET /themes/{surah_number}`, `GET /topics/for-ayas?keys=`
- `GET /related/{aya_key}`, `GET /phrase/{id}`, `GET /phrase/{id}/ayas`
- `GET /auth/login`, `GET /auth/callback`, `GET /auth/me`, `POST /auth/logout`
- `GET|PUT|DELETE /bookmarks/reading`, `GET /bookmarks`, `POST /bookmarks/notes`, `PUT|DELETE /bookmarks/notes/{id}`
