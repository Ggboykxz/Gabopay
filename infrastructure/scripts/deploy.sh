#!/bin/bash
set -e

echo "GABOPAY Deploy Script"
echo "======================="

if [ "$1" = "production" ]; then
    ENV_FILE=".env.production"
    COMPOSE_FILE="infrastructure/docker/docker-compose.prod.yml"
else
    ENV_FILE=".env"
    COMPOSE_FILE="infrastructure/docker/docker-compose.yml"
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found!"
    exit 1
fi

echo "Loading environment from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

echo "Building and starting services..."
docker compose -f $COMPOSE_FILE build
docker compose -f $COMPOSE_FILE up -d

echo "Waiting for services..."
sleep 5
for i in $(seq 1 12); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "API is healthy!"
        break
    fi
    echo "Waiting for API... ($i/12)"
    sleep 5
done

echo "Deployment complete!"
echo ""
echo "Services:"
docker compose -f $COMPOSE_FILE ps
