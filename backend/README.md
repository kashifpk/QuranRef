# QuranRef Backend

FastAPI-based backend service for the QuranRef application, providing REST APIs for Quran text search and retrieval.

## Tech Stack

- **Framework**: FastAPI with async/await support
- **Database**: ArangoDB (graph database)
- **Package Manager**: uv (ultra-fast Python package manager)
- **Python**: 3.12+
- **ORM**: arango-orm for document modeling
- **CLI**: Typer for management commands
- **Testing**: pytest with fixtures

## Project Structure

```
backend/
├── quranref/              # Main application package
│   ├── main.py            # FastAPI application entry point
│   ├── api.py             # REST API endpoints
│   ├── models.py          # ArangoDB document models
│   ├── cli.py             # Management CLI commands
│   ├── config.py          # Configuration management
│   └── database.py        # Database connection handling
├── data/                  # Quran text data files
│   ├── text/              # Arabic text and translations
│   └── surah_data.json    # Surah metadata
├── tests/                 # Test suite
├── .env                   # Environment variables
└── pyproject.toml         # Project dependencies (uv-compatible)
```

## Development Setup

### Docker Development (Recommended)

```bash
# From project root - start all services
./dev-docker.sh up

# Access backend container shell
./dev-docker.sh shell

# Inside container:
# Run tests
pytest

# Check code quality
ruff check
ruff format

# Run CLI commands
quranref-cli --help
```

The backend will be available at http://localhost:41148 with automatic reload on code changes.

### Direct Host Development

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Run development server with auto-reload
uv run fastapi dev quranref/main.py --host 0.0.0.0 --port 8000

# Or using uvicorn directly
uv run uvicorn quranref.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Run linting
uv run ruff check
uv run ruff format
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Application settings
ENVIRONMENT=development
DEBUG=true

# Database configuration
DB_HOSTS=http://localhost:8529   # Or http://arangodb:8529 for Docker
DB_USERNAME=quranref
DB_PASSWORD=your_password
DB_NAME=quranref

# Logging
LOGGING_ENABLED_FOR_PACKAGES=["quranref"]
```

## API Endpoints

The backend provides the following REST endpoints:

- `GET /api/v1/surahs` - List all Surahs with metadata
- `GET /api/v1/text/{surah_number}/{text_types}` - Get Surah text with translations
- `GET /api/v1/search/{term}/{search_lang}/{translation_langs}` - Search Quran text
- `GET /api/v1/words-by-letter/{letter}` - Browse words by starting letter
- `GET /api/v1/ayas-by-word/{word}/{languages}` - Get verses containing a word
- `GET /api/v1/info` - Application metadata

Interactive API documentation available at:
- Swagger UI: http://localhost:41148/docs
- ReDoc: http://localhost:41148/redoc

## CLI Commands

The backend includes a CLI for database management:

```bash
# Initialize database structure
quranref-cli db init

# Populate Surah metadata
quranref-cli db populate-surahs

# Import Quran text and translations
quranref-cli db import-text

# Create graph relationships
quranref-cli post-process link-ayas-to-surahs

# Extract and index words
quranref-cli post-process make-words

# Drop all collections (use with caution!)
quranref-cli db drop-all
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=quranref --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

The project uses `ruff` for linting and formatting:

```bash
# Check code style
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix

# Format code
uv run ruff format

# Type checking (if using mypy)
uv run mypy quranref
```

## Database Schema

The application uses ArangoDB with the following collections:

- **surahs**: Surah metadata (number, name, verses count, revelation place)
- **ayas**: Individual verses (surah_no, aya_no, text references)
- **texts**: Deduplicated text storage (hash-based)
- **words**: Extracted words with frequency counts
- **meta_info**: Application metadata and statistics

Graph relationships:
- Surahs → Ayas (has)
- Ayas → Words (contains)

## Dependencies Management

Using `uv` for dependency management:

```bash
# Add a new dependency
uv add package_name

# Add development dependency
uv add --dev package_name

# Update dependencies
uv sync

# Show dependency tree
uv tree

# Export requirements (if needed)
uv export > requirements.txt
```

## Performance Considerations

- Uses async/await for all database operations
- Text deduplication via SHA-256 hashing
- Strategic indexing on frequently queried fields
- Connection pooling for ArangoDB
- Response caching for static data (Surahs list)

## Troubleshooting

### Database Connection Issues
- Verify ArangoDB is running: `docker ps` or check http://localhost:18529
- Check credentials in `.env` file
- For Docker: use `http://arangodb:8529` as DB_HOSTS
- For host: use `http://localhost:8529` as DB_HOSTS

### Import/Migration Issues
- Ensure database is initialized: `quranref-cli db init`
- Check data files exist in `data/` directory
- Verify file permissions for data files

### Development Server Issues
- Port conflicts: Change port with `--port` flag
- Module not found: Run `uv sync` to install dependencies
- Auto-reload not working: Check file watchers limit on Linux