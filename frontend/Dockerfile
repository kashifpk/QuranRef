# Frontend development Dockerfile
FROM oven/bun:1

WORKDIR /app

# Copy package files
COPY package.json .
COPY bun.lockb .

# Install dependencies
RUN bun install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Start dev server
CMD ["bun", "run", "dev"]
# Frontend production Dockerfile
FROM oven/bun:1 as build

WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install
COPY . .
RUN bun run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
