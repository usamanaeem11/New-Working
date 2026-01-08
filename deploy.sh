#!/bin/bash
# WorkingTracker Master Deployment Script
# Deploys entire system: Database + Backend + Frontend + Mobile + Desktop

set -e

echo "=========================================="
echo "  WorkingTracker Deployment"
echo "=========================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required"; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "❌ PostgreSQL required"; exit 1; }
echo "✅ Prerequisites OK"
echo ""

# Database setup
echo "📊 Setting up database..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw workingtracker; then
    echo "Creating database..."
    createdb workingtracker
    createuser workingtracker -P || true
fi
echo "✅ Database ready"
echo ""

# Backend setup
echo "🔧 Setting up backend..."
cd services/api

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages --quiet

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "✅ Backend setup complete"
echo ""

# Frontend setup
echo "🌐 Setting up frontend..."
cd ../../services/web

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --silent
fi

echo "✅ Frontend setup complete"
echo ""

# Start services
echo "🚀 Starting services..."
echo ""

# Start backend in background
cd ../../services/api
nohup uvicorn app.main_complete:app --host 0.0.0.0 --port 8000 --ws websockets > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend
sleep 5

# Start frontend
cd ../../services/web
echo "✅ Frontend starting..."
npm start

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop backend: kill $BACKEND_PID"
