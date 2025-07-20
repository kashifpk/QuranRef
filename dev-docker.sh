#!/bin/bash

# QuranRef Docker Development Script
# Provides system-upgrade-proof development environment

usage() {
  echo "Usage: $0 [option]"
  echo "Options:"
  echo "  up       - Start all services in development mode"
  echo "  down     - Stop and remove all services"
  echo "  build    - Rebuild all images"
  echo "  logs     - Show logs from all services"
  echo "  backend  - Show backend logs only"
  echo "  frontend - Show frontend logs only"
  echo "  db       - Show database logs only"
  echo "  shell    - Open shell in backend container"
  echo "  clean    - Remove all containers, images, and volumes"
  echo "  help     - Show this help message"
}

check_docker() {
  if ! command -v docker > /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
  fi
  
  if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker."
    exit 1
  fi
}

case "$1" in
  up)
    check_docker
    echo "🚀 Starting QuranRef development environment..."
    docker compose -f docker-compose.dev.yml --env-file .env.dev up -d
    echo ""
    echo "✅ Development environment started!"
    echo "   Frontend: http://localhost:41149"
    echo "   Backend:  http://localhost:41148"
    echo "   ArangoDB: http://localhost:18529"
    echo ""
    echo "📝 To view logs: ./dev-docker.sh logs"
    echo "🛑 To stop: ./dev-docker.sh down"
    ;;
  down)
    check_docker
    echo "🛑 Stopping development environment..."
    docker compose -f docker-compose.dev.yml down
    echo "✅ Development environment stopped."
    ;;
  build)
    check_docker
    echo "🔨 Rebuilding development images..."
    docker compose -f docker-compose.dev.yml --env-file .env.dev build
    echo "✅ Images rebuilt successfully."
    ;;
  logs)
    check_docker
    docker compose -f docker-compose.dev.yml logs -f
    ;;
  backend)
    check_docker
    docker compose -f docker-compose.dev.yml logs -f backend
    ;;
  frontend)
    check_docker
    docker compose -f docker-compose.dev.yml logs -f frontend
    ;;
  db)
    check_docker
    docker compose -f docker-compose.dev.yml logs -f arangodb
    ;;
  shell)
    check_docker
    docker compose -f docker-compose.dev.yml exec backend bash
    ;;
  clean)
    check_docker
    echo "🧹 Cleaning up all Docker resources..."
    docker compose -f docker-compose.dev.yml down -v --remove-orphans
    docker system prune -f
    echo "✅ Cleanup completed."
    ;;
  help|*)
    usage
    ;;
esac