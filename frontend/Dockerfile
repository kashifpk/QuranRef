# Frontend production Dockerfile
FROM oven/bun:1 as build

WORKDIR /app
COPY frontend/package.json frontend/bun.lockb ./
RUN bun install
COPY frontend/ .
RUN bun run build

FROM nginx:alpine
# Copy from the actual build output location
COPY --from=build /static/frontend /usr/share/nginx/html
COPY config/nginx.prod.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
