# QuranRef Deployment Agent

## Purpose

This agent handles all deployment-related tasks for the QuranRef application, including building Docker images, pushing to registry, and deploying to Docker Swarm in production.

## Capabilities

- Build and tag Docker images for frontend and backend
- Push images to Docker registry
- Deploy to Docker Swarm using existing contexts
- Verify deployment status
- Handle rollbacks if needed
- Force service updates when necessary

## Context and Setup

### Docker Contexts

- **default**: Local development environment
- **production**: Production Docker Swarm (ssh://kashif@hosting_vps)

### Registry

- Registry URL: `localhost:5000`
- Images are tagged and pushed to this registry before deployment

### Stack Configuration

- Stack name: `quranref`
- Services: `quranref_frontend`, `quranref_backend`, `quranref_arangodb`
- Production URLs:
  - Frontend: <https://quranref.info>, <https://www.quranref.info>
  - API: <https://api.quranref.info>

## Standard Deployment Procedures

### 1. Quick Frontend Fix Deployment

When deploying a frontend fix (like the hamburger menu fix):

```bash
# Build the frontend image with a new version tag
docker build -f frontend/Dockerfile -t quranref-frontend:v[N] .
docker tag quranref-frontend:v[N] localhost:5000/quranref-frontend:v[N]

# Push to production registry
docker context use production
docker push localhost:5000/quranref-frontend:v[N]

# Update the service
docker service update quranref_frontend --image localhost:5000/quranref-frontend:v[N]
docker context use default
```

### 2. Full Deployment (Frontend + Backend)

Using the deployment script:

```bash
./deploy-to-swarm.sh full [version]
```

This script:

1. Builds both frontend and backend images
2. Tags them appropriately
3. Pushes to the registry
4. Deploys the stack to Docker Swarm
5. Verifies deployment status

### 3. Force Service Update

When you need to force a service restart without image changes:

```bash
docker context use production
docker service update --force quranref_frontend
docker context use default
```

### 4. Check Deployment Status

```bash
docker context use production
docker service ls | grep quranref
docker service ps quranref_frontend --format "table {{.Name}}\t{{.CurrentState}}"
docker service logs quranref_frontend --tail 20
docker context use default
```

## Known Issues and Solutions

### Issue: Nginx 404 Errors After Deployment

**Symptoms**: Getting 404 errors, logs show "/etc/nginx/html/index.html" not found

**Solution**:

1. Check if the nginx.prod.conf has correct server_name (should be `_` not `localhost`)
2. Ensure the Dockerfile copies files to `/usr/share/nginx/html`
3. Force update the service after fixing

### Issue: Image Not Found in Registry

**Symptoms**: "tag does not exist: localhost:5000/quranref-backend:vX"

**Solution**:

1. Manually build and tag the image
2. Push to registry before deployment
3. Use consistent version tags

### Issue: Service Not Converging

**Symptoms**: Service stuck in "Running X seconds ago" loop

**Solution**:

1. Check service logs for errors
2. Verify image can run locally
3. Check resource constraints on swarm nodes

## Deployment Checklist

Before deploying:

- [ ] Test changes locally using `./dev-docker.sh`
- [ ] Verify frontend builds successfully: `docker exec quranref_frontend_dev bun run build`
- [ ] Check for TypeScript errors (if frontend changes)
- [ ] Ensure no sensitive data in commits

During deployment:

- [ ] Use appropriate version tags (not just 'latest')
- [ ] Monitor service status during rollout
- [ ] Check logs for any errors
- [ ] Verify services are running: 2/2 replicas

After deployment:

- [ ] Test the production site: <https://www.quranref.info>
- [ ] Verify the specific fix/feature is working
- [ ] Check API endpoints if backend was updated
- [ ] Monitor for any errors in the first few minutes

## Environment-Specific Configurations

### Production Environment Variables

Frontend:

- `VITE_API_BASE_URL=https://api.quranref.info/api/v1`
- `VITE_ENVIRONMENT=production`
- `VITE_WEBSITE_BASE_URL=https://quranref.info`

Backend:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `DB_HOSTS=http://arangodb:8529`

### Traefik Routing

The production setup uses Traefik for routing:

- Frontend requests go to nginx containers
- `/api` requests are routed to backend containers
- SSL certificates are managed by Traefik

## Recovery Procedures

### Rollback to Previous Version

```bash
docker context use production
# Find the previous working version
docker service ps quranref_frontend --format "table {{.Image}}"
# Update to previous version
docker service update quranref_frontend --image localhost:5000/quranref-frontend:[previous-version]
docker context use default
```

### Emergency Service Restart

```bash
docker context use production
docker service scale quranref_frontend=0
sleep 5
docker service scale quranref_frontend=2
docker context use default
```

## Important Notes

1. **Always switch context back to default** after production operations
2. **Version tags are important** - avoid using 'latest' in production
3. **The nginx configuration** must use `server_name _` not `localhost` for production
4. **Frontend static files** are served from `/static/` path in production
5. **Build output location**: Frontend builds to `../static/frontend/` relative to frontend directory
6. **Registry push is required** before deployment - images must be in localhost:5000 registry

## Agent Instructions

When asked to deploy:

1. First determine what needs to be deployed (frontend, backend, or both)
2. Check current deployment status
3. Build and tag images with appropriate version numbers
4. Push to registry (with production context)
5. Deploy using either the script or manual commands
6. Verify deployment succeeded
7. Test the production site
8. Always return context to default

If deployment fails:

1. Check service logs for errors
2. Verify the image works locally
3. Check if it's a configuration issue (nginx, env vars)
4. Consider rolling back if necessary
5. Document any new issues discovered

Remember: The deployment process affects live production users. Always verify changes work locally first, use proper version tags, and monitor the deployment closely.
