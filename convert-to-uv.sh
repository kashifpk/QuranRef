#!/bin/bash

# Script to convert from Poetry to uv for the QuranRef project

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc  # Reload shell configuration
fi

# Install necessary packages
echo "Installing necessary packages..."
uv pip install pyproject-metadata hatchling

echo "Converting Poetry project to uv..."

# Go to backend directory
cd backend || exit

# Create requirements.txt from pyproject.toml
echo "Generating requirements.txt from pyproject.toml..."
python -c "import pyproject_metadata; md = pyproject_metadata.StandardMetadata.from_pyproject('pyproject.toml'); print('\n'.join(map(str, md.requires_dist or [])))" > requirements.txt

# Install dependencies with uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create uv-compatible pyproject.toml
echo "Creating uv-compatible pyproject.toml..."
cat > pyproject.toml.uv << 'EOF'
[project]
name = "quranref"
version = "2.0.0"
description = ""
authors = [
    {name = "Kashif Iftikhar", email = "kashif@compulife.com.pk"}
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.112.2",
    "pydantic-settings>=2.4.0",
    "typer>=0.12.5",
    "jinja2>=3.1.4",
    "arango-orm>=1.1.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.6.3",
    "bandit>=1.7.9",
    "ipython>=8.27.0",
    "pre-commit>=3.8.0",
]
test = [
    "pytest>=8.3.2",
    "pytest-cov>=5.0.0",
    "pytest-env>=1.1.3",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
quranref-cli = "quranref.cli:main"

[tool.bandit]
exclude_dirs = ["tests"]
# B101 = ignore assert_used
# B404 = allow use of sub process module
# B603 = allow calls to Popen with shell=False
skips = ["B101", "B404", "B603"]

[tool.ruff]
line-length = 100
src = ["quranref"]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "--cov=quranref --cov-fail-under=50"
testpaths = [
    "tests",
]

filterwarnings = [
    "ignore::DeprecationWarning",
]

env = [
    "QURANREF_TESTING=true"
]
EOF

# Create a backup of original poetry files
echo "Creating backups of poetry files..."
cp pyproject.toml pyproject.toml.poetry.bak
cp poetry.lock poetry.lock.bak

# Replace pyproject.toml with uv-compatible version
echo "Replacing pyproject.toml with uv-compatible version..."
mv pyproject.toml.uv pyproject.toml

# Install the project in development mode
echo "Installing the project in development mode..."
uv pip install -e .

echo "Conversion complete!"
echo "You can now run the backend with: python -m fastapi dev quranref/main.py --host 0.0.0.0 --port 8000"
echo "Note: Your original poetry files have been backed up with .bak extension."