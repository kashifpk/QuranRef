#!/bin/bash

# QuranRef Docker Swarm Deployment Script
# This script deploys QuranRef to production using Docker Context

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTEXT_NAME="production"
REGISTRY_URL="localhost:5000"
STACK_NAME="quranref"

# Handle version parameter properly
case "$1" in
    setup|build|push|deploy|full|init-db|status)
        VERSION=${2:-latest}
        ;;
    *)
        VERSION=${1:-latest}
        ;;
esac

echo -e "${BLUE}QuranRef Docker Swarm Deployment${NC}"
echo "=================================="

# Step 1: Setup Docker Context (one-time setup)
setup_context() {
    echo -e "${YELLOW}Setting up Docker context...${NC}"
    
    # Check if context already exists
    if docker context ls | grep -q "$CONTEXT_NAME"; then
        echo -e "${GREEN}✓ Docker context '$CONTEXT_NAME' already exists${NC}"
    else
        echo "Creating Docker context '$CONTEXT_NAME'..."
        echo "You'll need your production server's SSH details:"
        read -p "Enter SSH connection string (e.g., user@server.com): " SSH_CONNECTION
        docker context create "$CONTEXT_NAME" \
            --description "Production Docker Swarm" \
            --docker "host=ssh://$SSH_CONNECTION"
        echo -e "${GREEN}✓ Docker context created${NC}"
    fi
}

# Step 2: Build images locally
build_images() {
    echo -e "${YELLOW}Building production images...${NC}"
    
    # Build backend
    echo "Building backend image..."
    docker build -t quranref-backend:$VERSION -f backend/Dockerfile backend/
    
    # Build frontend
    echo "Building frontend image..."
    docker build -t quranref-frontend:$VERSION -f frontend/Dockerfile .
    
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Step 3: Tag images for registry
tag_images() {
    echo -e "${YELLOW}Tagging images for registry...${NC}"
    
    docker tag quranref-backend:$VERSION $REGISTRY_URL/quranref-backend:$VERSION
    docker tag quranref-backend:$VERSION $REGISTRY_URL/quranref-backend:latest
    
    docker tag quranref-frontend:$VERSION $REGISTRY_URL/quranref-frontend:$VERSION
    docker tag quranref-frontend:$VERSION $REGISTRY_URL/quranref-frontend:latest
    
    echo -e "${GREEN}✓ Images tagged${NC}"
}

# Step 4: Push to registry (using production context)
push_to_registry() {
    echo -e "${YELLOW}Pushing images to production registry...${NC}"
    
    # Switch to production context
    docker context use "$CONTEXT_NAME"
    
    # Push images
    docker push $REGISTRY_URL/quranref-backend:$VERSION
    docker push $REGISTRY_URL/quranref-backend:latest
    docker push $REGISTRY_URL/quranref-frontend:$VERSION
    docker push $REGISTRY_URL/quranref-frontend:latest
    
    echo -e "${GREEN}✓ Images pushed to registry${NC}"
}

# Step 5: Deploy stack
deploy_stack() {
    echo -e "${YELLOW}Deploying stack to Docker Swarm...${NC}"
    
    # Ensure we're using production context
    docker context use "$CONTEXT_NAME"
    
    # Check if .env.production files exist
    if [[ ! -f backend/.env.production ]]; then
        echo -e "${RED}Error: backend/.env.production not found${NC}"
        echo "Please create it from backend/.env"
        exit 1
    fi
    
    if [[ ! -f frontend/.env.production ]]; then
        echo -e "${RED}Error: frontend/.env.production not found${NC}"
        echo "Please create it from frontend/.env"
        exit 1
    fi
    
    # Deploy the stack
    docker stack deploy -c docker-compose.swarm.yml "$STACK_NAME"
    
    echo -e "${GREEN}✓ Stack deployed${NC}"
}

# Step 6: Check deployment status
check_status() {
    echo -e "${YELLOW}Checking deployment status...${NC}"
    
    docker context use "$CONTEXT_NAME"
    
    echo ""
    echo "Stack services:"
    docker stack services "$STACK_NAME"
    
    echo ""
    echo "Service status:"
    docker stack ps "$STACK_NAME" --no-trunc
    
    echo ""
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    echo ""
    echo "Your application should be accessible at:"
    echo "  - Frontend: https://quranref.info"
    echo "  - API: https://api.quranref.info"
    echo ""
    echo "To initialize the database (first time only), run:"
    echo "  ./deploy-to-swarm.sh init-db"
}

# Initialize database (first deployment only)
init_database() {
    echo -e "${YELLOW}Initializing database...${NC}"
    
    docker context use "$CONTEXT_NAME"
    
    # Get backend container ID
    BACKEND_ID=$(docker ps -q -f "name=${STACK_NAME}_backend")
    
    if [[ -z "$BACKEND_ID" ]]; then
        echo -e "${RED}Error: Backend container not found${NC}"
        exit 1
    fi
    
    # Run initialization commands
    echo "Running database initialization..."
    docker exec "$BACKEND_ID" quranref-cli db init
    docker exec "$BACKEND_ID" quranref-cli db populate-surahs
    docker exec "$BACKEND_ID" quranref-cli db import-text
    docker exec "$BACKEND_ID" quranref-cli post-process link-ayas-to-surahs
    docker exec "$BACKEND_ID" quranref-cli post-process make-words
    
    echo -e "${GREEN}✓ Database initialized${NC}"
}

# Main execution
case "${1:-deploy}" in
    setup)
        setup_context
        ;;
    build)
        build_images
        ;;
    push)
        build_images
        tag_images
        push_to_registry
        ;;
    deploy)
        deploy_stack
        check_status
        ;;
    full)
        setup_context
        build_images
        tag_images
        push_to_registry
        deploy_stack
        check_status
        ;;
    init-db)
        init_database
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {setup|build|push|deploy|full|init-db|status} [version]"
        echo ""
        echo "Commands:"
        echo "  setup    - Configure Docker context for remote deployment"
        echo "  build    - Build production images locally"
        echo "  push     - Build, tag, and push images to registry"
        echo "  deploy   - Deploy stack to Docker Swarm"
        echo "  full     - Run complete deployment (setup, build, push, deploy)"
        echo "  init-db  - Initialize database (first deployment only)"
        echo "  status   - Check deployment status"
        echo ""
        echo "Examples:"
        echo "  $0 full           # Complete deployment with 'latest' tag"
        echo "  $0 full v1.2.3    # Complete deployment with version tag"
        echo "  $0 deploy         # Just deploy (assumes images exist)"
        echo "  $0 init-db        # Initialize database after first deployment"
        exit 1
        ;;
esac

# Switch back to default context
docker context use default