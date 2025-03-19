# Configuration Files

This directory contains configuration files for the QuranRef application.

## Files

- **nginx.conf**: Nginx configuration for the production server
- **.env.example**: Example environment variables file with placeholders
- **.env.prod**: Production environment variables (sensitive data should be replaced before deployment)

## Usage

- The nginx.conf file is used in the frontend Dockerfile to configure the Nginx server
- Copy .env.example to .env in the project root to set up your development environment
- For production deployment, review and modify .env.prod as needed