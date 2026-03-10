#!/bin/bash
set -e

# Change to the script's directory (project root)
cd "$(dirname "$0")"

echo "=== FactAnchor Start Script ==="

# 1. Check for .env file
if [ ! -f .env ]; then
    echo "❌ Missing .env file. Please copy .env.example to .env and fill it!"
    exit 1
fi

# Function to check placeholder
check_placeholder() {
    local key=$1
    if grep -q "^${key}=PLACEHOLDER" .env; then
        echo "❌ ERROR: You must replace the PLACEHOLDER value for $key in .env"
        exit 1
    fi
}

# Check API Keys
check_placeholder "PINECONE_API_KEY"
check_placeholder "NVIDIA_API_KEY"
check_placeholder "JWT_SECRET_KEY"

# Grab the credentials directly to inject during migration
export $(grep -v '^#' .env | xargs)

# 2. Run docker compose
echo "🚀 Building and starting Docker containers..."
docker compose up --build -d

# 3. Wait for database health
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker exec fa-postgres-1 pg_isready -U factanchor_app &>/dev/null; do
    printf "."
    sleep 2
done
echo -e "\n✅ Database is up"

# 4. Database Migrations
echo "🔄 Running Alembic database migrations..."
# Using docker exec on the API container
docker exec fa-api-1 alembic upgrade head
echo "✅ Migrations complete"

# 5. Financial Seed Data
echo "🌱 Seeding PostgreSQL with financial data..."
docker exec -i fa-postgres-1 psql -U factanchor_app factanchor < backend/seeds/financial_data.sql
echo "✅ SQL seed data complete"

# 6. Pinecone Seed Script
echo "🌲 Waiting for Python environment and seeding Pinecone..."
# Run the python script locally (or via the container). Doing it via container ensures deps map perfectly.
docker exec fa-api-1 python /app/scripts/seed_pinecone.py

# 7. Final output
echo ""
echo "🎉 Setup Complete! FactAnchor is ready."
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 API Docs:  http://localhost:8000/docs"
echo "Celery Flower (workers): http://localhost:5555"
