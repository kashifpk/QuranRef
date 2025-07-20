#!/bin/bash

# QuranRef Podman to Docker Migration Script
# This script helps migrate ArangoDB data from Podman container to Docker container

set -e

BACKUP_DIR="./data_migration_backup"
PODMAN_CONTAINER="quranref_arangodb"
DOCKER_CONTAINER="quranref_arangodb_dev"

usage() {
  echo "Usage: $0 [option]"
  echo "Options:"
  echo "  backup   - Backup data from existing Podman ArangoDB"
  echo "  restore  - Restore data to new Docker ArangoDB"
  echo "  migrate  - Complete migration (backup + restore)"
  echo "  check    - Check if Podman container has data"
  echo "  clean    - Clean up backup files"
  echo "  help     - Show this help message"
}

check_podman_data() {
  echo "🔍 Checking for existing Podman ArangoDB data..."
  
  if ! command -v podman > /dev/null; then
    echo "❌ Podman not found. Migration not needed."
    return 1
  fi
  
  if ! podman ps -a --filter "name=$PODMAN_CONTAINER" --format "{{.Names}}" | grep -q "$PODMAN_CONTAINER"; then
    echo "❌ Podman container '$PODMAN_CONTAINER' not found. Migration not needed."
    return 1
  fi
  
  echo "✅ Found Podman container '$PODMAN_CONTAINER'"
  
  # Start the container if it's not running
  if ! podman ps --filter "name=$PODMAN_CONTAINER" --format "{{.Names}}" | grep -q "$PODMAN_CONTAINER"; then
    echo "📦 Starting Podman ArangoDB container..."
    podman start "$PODMAN_CONTAINER"
    sleep 5
  fi
  
  # Check if it has QuranRef data
  echo "🔍 Checking for QuranRef database..."
  if podman exec "$PODMAN_CONTAINER" arangosh --server.password="" --javascript.execute-string "db._name()" 2>/dev/null | grep -q "quranref"; then
    echo "✅ Found QuranRef data in Podman container!"
    return 0
  else
    echo "❓ Podman container exists but may not have QuranRef data."
    echo "   You can still proceed with migration to be safe."
    return 0
  fi
}

backup_podman_data() {
  echo "💾 Starting backup from Podman ArangoDB..."
  
  if ! check_podman_data; then
    echo "❌ No Podman data to backup."
    return 1
  fi
  
  # Create backup directory
  mkdir -p "$BACKUP_DIR"
  
  echo "📦 Creating database dump..."
  # Use arangodump to create a backup
  podman exec "$PODMAN_CONTAINER" arangodump \
    --server.endpoint tcp://localhost:8529 \
    --server.password="" \
    --output-directory /tmp/backup \
    --overwrite true \
    --include-system-collections false
  
  # Copy backup from container to host
  echo "📤 Copying backup from container..."
  podman cp "$PODMAN_CONTAINER:/tmp/backup" "$BACKUP_DIR/"
  
  echo "✅ Backup completed: $BACKUP_DIR/backup/"
  ls -la "$BACKUP_DIR/backup/"
}

restore_docker_data() {
  echo "📥 Starting restore to Docker ArangoDB..."
  
  if [ ! -d "$BACKUP_DIR/backup" ]; then
    echo "❌ No backup found at $BACKUP_DIR/backup/"
    echo "   Run './migrate-podman-to-docker.sh backup' first"
    return 1
  fi
  
  # Start Docker environment if not running
  echo "🚀 Ensuring Docker environment is running..."
  ./dev-docker.sh up
  
  # Wait for ArangoDB to be ready
  echo "⏳ Waiting for Docker ArangoDB to be ready..."
  until curl -s http://localhost:18529/_api/version > /dev/null 2>&1; do
    sleep 2
    echo -n "."
  done
  echo " Ready!"
  
  # Copy backup to Docker container
  echo "📤 Copying backup to Docker container..."
  docker cp "$BACKUP_DIR/backup" "$DOCKER_CONTAINER:/tmp/"
  
  # Restore the database
  echo "📥 Restoring database..."
  docker exec "$DOCKER_CONTAINER" arangorestore \
    --server.endpoint tcp://localhost:8529 \
    --server.password="Test123!" \
    --input-directory /tmp/backup \
    --create-database true
  
  echo "✅ Restore completed!"
}

complete_migration() {
  echo "🔄 Starting complete migration from Podman to Docker..."
  
  if check_podman_data; then
    backup_podman_data
    restore_docker_data
    echo ""
    echo "🎉 Migration completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Test your Docker development environment: ./dev-docker.sh up"
    echo "2. Verify data integrity by checking your application"
    echo "3. Once satisfied, you can clean up: ./migrate-podman-to-docker.sh clean"
  else
    echo "ℹ️  No migration needed. You can start fresh with Docker."
    echo "   Run: ./dev-docker.sh up"
  fi
}

clean_backup() {
  echo "🧹 Cleaning up backup files..."
  if [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
    echo "✅ Backup files cleaned up."
  else
    echo "ℹ️  No backup files to clean."
  fi
}

case "$1" in
  backup)
    backup_podman_data
    ;;
  restore)
    restore_docker_data
    ;;
  migrate)
    complete_migration
    ;;
  check)
    check_podman_data
    ;;
  clean)
    clean_backup
    ;;
  help|*)
    usage
    ;;
esac