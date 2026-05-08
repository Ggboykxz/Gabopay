#!/bin/bash
set -e

echo "🚀 GABOPAY Setup Script"
echo "========================"

if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys and secrets!"
fi

echo "📦 Installing dependencies..."

if command -v npm &> /dev/null; then
    echo "  - Installing Node.js dependencies..."
    npm install
else
    echo "  ⚠️  npm not found, skipping Node.js dependencies"
fi

if command -v poetry &> /dev/null; then
    echo "  - Installing Python dependencies..."
    poetry install
else
    echo "  ⚠️  poetry not found, skipping Python dependencies"
fi

echo "🐳 Starting Docker services..."
docker-compose -f infrastructure/docker/docker-compose.yml up -d postgres redis

echo "⏳ Waiting for PostgreSQL..."
until docker-compose -f infrastructure/docker/docker-compose.yml exec -T postgres pg_isready -U postgres; do
    sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "⏳ Waiting for Redis..."
until docker-compose -f infrastructure/docker/docker-compose.yml exec -T redis redis-cli ping; do
    sleep 1
done
echo "✅ Redis is ready!"

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: docker-compose -f infrastructure/docker/docker-compose.yml up"
echo "  3. Visit http://localhost:3000 for dashboard"