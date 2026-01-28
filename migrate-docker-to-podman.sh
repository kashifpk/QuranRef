#!/bin/bash

# Migrate QuranRef ArangoDB data from Docker to Podman
# This script copies the database volume from Docker's storage to Podman's storage

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_info() { printf "${CYAN}ℹ ${NC}%s\n" "$1"; }
print_success() { printf "${GREEN}✓${NC} %s\n" "$1"; }
print_warning() { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
print_error() { printf "${RED}✗${NC} %s\n" "$1"; }

# Configuration
DOCKER_VOLUME_NAME="quranref_arangodb_dev_data"
PODMAN_VOLUME_NAME="quranref_arangodb_dev_data"
DOCKER_VOLUME_PATH="/var/lib/docker/volumes/${DOCKER_VOLUME_NAME}/_data"

echo ""
echo "=========================================="
echo "  QuranRef: Docker to Podman Migration"
echo "=========================================="
echo ""

# Check if running as regular user (we'll use sudo where needed)
if [ "$EUID" -eq 0 ]; then
    print_error "Please run this script as a regular user (not root)."
    print_info "The script will use sudo where needed."
    exit 1
fi

# Check if Docker volume exists (need sudo to access Docker's storage)
if ! sudo test -d "$DOCKER_VOLUME_PATH"; then
    print_error "Docker volume not found at: $DOCKER_VOLUME_PATH"
    print_info "Available Docker volumes:"
    sudo ls -la /var/lib/docker/volumes/ | grep quran || echo "  (none found)"
    exit 1
fi

# Show Docker volume info
DOCKER_SIZE=$(sudo du -sh "$DOCKER_VOLUME_PATH" 2>/dev/null | cut -f1)
print_info "Source Docker volume: $DOCKER_VOLUME_NAME ($DOCKER_SIZE)"

# Check if Podman is available
if ! command -v podman &>/dev/null; then
    print_error "Podman is not installed."
    exit 1
fi

# Check if podman compose is available
if ! podman compose version &>/dev/null 2>&1 && ! command -v podman-compose &>/dev/null; then
    print_error "Neither 'podman compose' nor 'podman-compose' is available."
    exit 1
fi

# Determine compose command
if command -v podman-compose &>/dev/null; then
    COMPOSE_CMD="podman-compose"
else
    COMPOSE_CMD="podman compose"
fi

print_info "Using: $COMPOSE_CMD"

# Check if services are running and stop them
if podman ps --format "{{.Names}}" 2>/dev/null | grep -q "quranref"; then
    print_warning "QuranRef containers are running. Stopping them..."
    $COMPOSE_CMD -f docker-compose.dev.yml down
fi

# Create the Podman volume if it doesn't exist
print_info "Creating Podman volume: $PODMAN_VOLUME_NAME"
podman volume create "$PODMAN_VOLUME_NAME" 2>/dev/null || true

# Get Podman volume mount point
PODMAN_VOLUME_PATH=$(podman volume inspect "$PODMAN_VOLUME_NAME" --format '{{.Mountpoint}}')

if [ -z "$PODMAN_VOLUME_PATH" ]; then
    print_error "Failed to get Podman volume mount point."
    exit 1
fi

print_info "Target Podman volume path: $PODMAN_VOLUME_PATH"

# Check if Podman volume already has data
if [ -n "$(ls -A "$PODMAN_VOLUME_PATH" 2>/dev/null)" ]; then
    print_warning "Podman volume already contains data!"
    read -p "Overwrite existing data? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_info "Migration cancelled."
        exit 0
    fi
    print_info "Clearing existing Podman volume data..."
    rm -rf "${PODMAN_VOLUME_PATH:?}"/*
fi

# Copy data from Docker to Podman
print_info "Copying data from Docker to Podman..."
print_info "This may take a moment..."

sudo cp -a "${DOCKER_VOLUME_PATH}/." "${PODMAN_VOLUME_PATH}/"

# Fix ownership for rootless Podman
print_info "Fixing permissions for Podman..."
sudo chown -R $(id -u):$(id -g) "$PODMAN_VOLUME_PATH"

# Verify the copy
PODMAN_SIZE=$(du -sh "$PODMAN_VOLUME_PATH" 2>/dev/null | cut -f1)
print_success "Migration complete!"
echo ""
print_info "Docker volume size: $DOCKER_SIZE"
print_info "Podman volume size: $PODMAN_SIZE"
echo ""

# Offer to start services
read -p "Start QuranRef services now? (Y/n): " start_services
if [ "$start_services" != "n" ] && [ "$start_services" != "N" ]; then
    print_info "Starting services..."
    ./devcon up
else
    print_info "You can start services later with: ./devcon up"
fi
