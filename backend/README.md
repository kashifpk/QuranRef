# QuranRef Backend

This directory contains all the backend code for the QuranRef application.

## Structure

- `quranref/`: Main Python package containing the application code
- `data/`: Data files used by the application
- `tests/`: Test files for the backend code
- `poetry.toml`: Poetry configuration
- `pyproject.toml`: Project configuration
- `poetry.lock`: Dependency lock file

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