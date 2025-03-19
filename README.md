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
│   ├── Dockerfile        # Backend Dockerfile
│   └── pyproject.toml    # Python dependencies
├── frontend/             # Vue.js frontend
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   ├── .env              # Frontend environment variables
│   ├── tsconfig.*.json   # TypeScript configuration
│   ├── vite.config.ts    # Vite configuration
│   ├── Dockerfile        # Frontend production Dockerfile
│   ├── Dockerfile-dev    # Frontend development Dockerfile
│   ├── package.json      # Frontend dependencies
│   └── bun.lockb         # Frontend lock file
├── config/               # Configuration files
│   ├── nginx.conf        # Nginx configuration
│   ├── .env.example      # Example environment variables
│   └── .env.prod         # Production environment variables
├── docker-compose.yml    # Docker compose configuration
├── docker-compose-dev.yml # Development Docker compose
├── docker-compose.prod.yml # Production Docker compose
└── README.md             # Project documentation
```

## Development Setup

1. The project uses separate environment files:
   - `backend/.env` for backend configuration
   - `frontend/.env` for frontend configuration

2. Start the development environment:
```bash
docker compose -f docker-compose-dev.yml up --build
```

3. Access the services:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - ArangoDB: http://localhost:8529

## Production Deployment

1. Build the production images:
```bash
docker compose -f docker-compose.prod.yml build
```

2. Deploy the stack:
```bash
docker compose -f docker-compose.prod.yml up -d
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
