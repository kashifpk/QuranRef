# QuranRef Production Deployment Guide

This guide explains how to deploy QuranRef to production using Docker Context and Docker Swarm with Traefik.

## Why Docker Context?

Docker Context allows you to deploy directly from your local machine to a remote Docker Swarm without SSH access. Benefits:

- **No SSH needed**: Deploy from your local machine
- **Secure**: Uses SSH tunneling for Docker commands
- **Efficient**: Build locally, push to registry, deploy remotely
- **GitOps-friendly**: Can be integrated with CI/CD pipelines
- **Rollback support**: Docker Swarm handles rolling updates and rollbacks

## Architecture Overview

```
Your Machine                    Production Server
    │                                │
    ├─ Build Images                  ├─ Docker Swarm
    ├─ Push to Registry ────────────►├─ Local Registry (:5000)
    └─ Deploy via Context            ├─ Traefik (SSL/Routing)
                                     ├─ QuranRef Backend
                                     ├─ QuranRef Frontend
                                     └─ ArangoDB
```

## Prerequisites

1. **Local Machine**:
   - Docker installed
   - SSH access to production server
   - Project source code

2. **Production Server**:
   - Docker Swarm initialized
   - Traefik deployed (already running)
   - Local Docker registry on port 5000

## Quick Deployment

For a complete deployment from scratch:

```bash
# One command does everything
./deploy-to-swarm.sh full

# First time only: Initialize database
./deploy-to-swarm.sh init-db
```

## Step-by-Step Deployment

### 1. Initial Setup (One-time)

```bash
# Setup Docker context for remote deployment
./deploy-to-swarm.sh setup

# When prompted, enter your SSH connection string
# Example: user@your-server.com
```

### 2. Configure Production Environment

```bash
# Copy and edit production environment files
cp backend/.env backend/.env.production
cp frontend/.env frontend/.env.production

# Edit the files with production values:
# - Database passwords
# - API URLs (https://api.quranref.info)
# - Secret keys
```

### 3. Build and Deploy

```bash
# Complete deployment process
./deploy-to-swarm.sh full

# Or do it step by step:
./deploy-to-swarm.sh build    # Build images
./deploy-to-swarm.sh push     # Push to registry
./deploy-to-swarm.sh deploy   # Deploy stack
```

### 4. Initialize Database (First Deployment Only)

```bash
# Run database initialization
./deploy-to-swarm.sh init-db
```

### 5. Check Deployment Status

```bash
# View deployment status
./deploy-to-swarm.sh status

# Or manually check:
docker context use production
docker stack services quranref
docker stack ps quranref
```

## Deployment Commands

| Command | Description |
|---------|-------------|
| `./deploy-to-swarm.sh setup` | Configure Docker context |
| `./deploy-to-swarm.sh build` | Build production images |
| `./deploy-to-swarm.sh push` | Push images to registry |
| `./deploy-to-swarm.sh deploy` | Deploy to Docker Swarm |
| `./deploy-to-swarm.sh full` | Complete deployment |
| `./deploy-to-swarm.sh init-db` | Initialize database |
| `./deploy-to-swarm.sh status` | Check deployment status |

## Version Management

Deploy specific versions:

```bash
# Deploy version 1.2.3
./deploy-to-swarm.sh full 1.2.3

# Deploy latest
./deploy-to-swarm.sh full latest
```

## URLs and Access

After deployment, your application will be accessible at:

- **Frontend**: https://quranref.info
- **API**: https://api.quranref.info
- **API Docs**: https://api.quranref.info/docs

SSL certificates are automatically managed by Traefik via Let's Encrypt.

## Rolling Updates

Docker Swarm handles rolling updates automatically:

```bash
# Deploy new version
./deploy-to-swarm.sh full v1.2.4

# Swarm will:
# 1. Start new containers
# 2. Health check new containers
# 3. Route traffic to new containers
# 4. Stop old containers
```

## Rollback

If something goes wrong:

```bash
# Switch to production context
docker context use production

# Rollback the service
docker service rollback quranref_backend
docker service rollback quranref_frontend
```

## Monitoring

```bash
# View logs
docker context use production
docker service logs quranref_backend
docker service logs quranref_frontend

# Scale services
docker service scale quranref_backend=3
docker service scale quranref_frontend=3
```

## Troubleshooting

### Context Connection Issues

```bash
# Test context connection
docker context use production
docker info

# Recreate context if needed
docker context rm production
./deploy-to-swarm.sh setup
```

### Registry Push Issues

```bash
# Check registry is accessible
docker context use production
curl http://localhost:5000/v2/_catalog

# Push manually if needed
docker context use production
docker push localhost:5000/quranref-backend:latest
```

### Service Not Starting

```bash
# Check service logs
docker context use production
docker service logs quranref_backend --tail 50

# Check service status
docker service ps quranref_backend --no-trunc
```

## CI/CD Integration

The deployment script can be integrated with CI/CD:

```yaml
# Example GitHub Actions
- name: Deploy to Production
  run: |
    # Setup Docker context using secrets
    echo "${{ secrets.SSH_KEY }}" > ~/.ssh/deploy_key
    chmod 600 ~/.ssh/deploy_key
    docker context create production --docker "host=ssh://user@server"
    
    # Deploy
    ./deploy-to-swarm.sh full ${{ github.event.release.tag_name }}
```

## Security Considerations

1. **Environment Files**: Never commit `.env.production` files
2. **Registry**: Local registry should only be accessible from Swarm nodes
3. **Secrets**: Use Docker secrets for sensitive data
4. **Network**: Internal network isolates database from internet
5. **HTTPS**: All traffic encrypted via Traefik

## Backup and Recovery

```bash
# Backup database
docker context use production
docker exec $(docker ps -q -f name=quranref_db) \
  arangodump --server.endpoint tcp://localhost:8529 \
  --output-directory /backup

# Copy backup locally
docker cp $(docker ps -q -f name=quranref_db):/backup ./backup
```

## Alternative Deployment Methods

While Docker Context is recommended, alternatives include:

1. **GitHub Actions**: Automated deployment on push/release
2. **GitLab CI/CD**: Similar to GitHub Actions
3. **Ansible**: Configuration management and deployment
4. **Manual SSH**: Traditional deployment (not recommended)

Docker Context provides the best balance of simplicity, security, and power for your Docker Swarm setup.