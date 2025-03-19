# QuranRef Frontend

This directory contains all the frontend code for the QuranRef application.

## Structure

- `src/`: Source code for the Vue.js application
- `public/`: Static assets
- `.env`: Frontend environment variables
- `config/`: Configuration files
- `tsconfig.*.json`: TypeScript configuration files

## Environment Variables

The frontend uses these environment variables in .env:

- `STATIC_URL`: URL for static assets
- `VITE_API_BASE_URL`: Base URL for API requests
- `VITE_WEBSITE_BASE_URL`: Base URL for the website

## Development

To run the development server:

```bash
cd frontend
npm run dev
```

## Building

To build the frontend:

```bash
cd frontend
npm run build
```