# QuranRef Backend

This directory contains all the backend code for the QuranRef application.

## Structure

- `quranref/`: Main Python package containing the application code
- `data/`: Data files used by the application
- `tests/`: Test files for the backend code
- `.env`: Backend environment variables
- `poetry.toml`: Poetry configuration
- `pyproject.toml`: Project configuration
- `poetry.lock`: Dependency lock file

## Environment Variables

The backend uses these environment variables in .env:

- `ENVIRONMENT`: Development/production setting
- `DEBUG`: Debug mode flag
- `DB_HOSTS`: ArangoDB connection string
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `LOGGING_ENABLED_FOR_PACKAGES`: Logger configuration

## Development

To set up the development environment:

```bash
cd backend
poetry install
poetry shell
```

## Running

To run the backend server:

```bash
cd backend
uvicorn quranref.main:app --reload
```