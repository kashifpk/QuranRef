# Quran Reference

Online easily accessible searchable reference of the Holy Quran and its translations.

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── quranref/         # Application code
│   ├── Dockerfile        # Backend Dockerfile
│   └── pyproject.toml    # Python dependencies
├── frontend/             # Vue.js frontend
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   ├── Dockerfile-dev    # Frontend development Dockerfile
│   ├── package.json      # Frontend dependencies
│   └── bun.lockb         # Frontend lock file
├── docker-compose.yml    # Docker compose configuration
└── README.md             # Project documentation
```

## Development Setup

1. Create `.env` files:
   - `backend/.env` for backend configuration
   - `frontend/.env` for frontend configuration

2. Start the development environment:
```bash
docker compose up --build
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
docker stack deploy -c docker-compose.prod.yml quranref
```

## Environment Variables

### Backend
- `DB_HOSTS`: ArangoDB connection string
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name

### Frontend
- `VITE_API_BASE_URL`: Base URL for API requests
