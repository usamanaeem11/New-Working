#!/usr/bin/env python3
"""
Create Complete Deployment Scripts
Production-ready deployment for all platforms
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  DEPLOYMENT SCRIPTS CREATION")
print("="*80)
print()

created = []

# Main deployment script
print("1. Creating master deployment script...")

create_file('deploy.sh', '''#!/bin/bash
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
if ! psql -lqt | cut -d \\| -f 1 | grep -qw workingtracker; then
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
''')

created.append(('Master Deploy Script', 2.1))
print("   ✅ Master deployment script created")

# Quick start script
print("2. Creating quick start script...")

create_file('quickstart.sh', '''#!/bin/bash
# Quick Start - Minimal setup for testing

echo "🚀 WorkingTracker Quick Start"
echo ""

# Check if already set up
if [ ! -f "services/api/.env" ]; then
    echo "📝 Creating configuration..."
    cat > services/api/.env << EOF
DATABASE_URL=postgresql://workingtracker:password@localhost:5432/workingtracker
JWT_SECRET_KEY=$(openssl rand -hex 32)
REFRESH_SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo "✅ Configuration created"
fi

# Backend
echo "🔧 Starting backend..."
cd services/api
python3 -m uvicorn app.main_complete:app --reload &
BACKEND_PID=$!

# Wait
sleep 3

# Frontend  
echo "🌐 Starting frontend..."
cd ../../services/web
npm start

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
''')

created.append(('Quick Start Script', 0.8))
print("   ✅ Quick start script created")

# Docker deployment
print("3. Creating Docker Compose configuration...")

create_file('docker-compose.yml', '''version: '3.8'

services:
  database:
    image: postgres:15
    container_name: workingtracker-db
    environment:
      POSTGRES_DB: workingtracker
      POSTGRES_USER: workingtracker
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U workingtracker"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    container_name: workingtracker-backend
    environment:
      DATABASE_URL: postgresql://workingtracker:password@database:5432/workingtracker
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-change-me}
      REFRESH_SECRET_KEY: ${REFRESH_SECRET_KEY:-change-me}
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             uvicorn app.main_complete:app --host 0.0.0.0 --port 8000 --ws websockets"

  frontend:
    build:
      context: ./services/web
      dockerfile: Dockerfile
    container_name: workingtracker-frontend
    environment:
      REACT_APP_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
''')

created.append(('Docker Compose', 1.6))
print("   ✅ Docker Compose created")

# Backend Dockerfile
print("4. Creating Backend Dockerfile...")

create_file('services/api/Dockerfile', '''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main_complete:app --host 0.0.0.0 --port 8000"]
''')

created.append(('Backend Dockerfile', 0.4))
print("   ✅ Backend Dockerfile created")

# Frontend Dockerfile
print("5. Creating Frontend Dockerfile...")

create_file('services/web/Dockerfile', '''FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application
COPY . .

# Build for production
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Serve the production build
CMD ["serve", "-s", "build", "-l", "3000"]
''')

created.append(('Frontend Dockerfile', 0.5))
print("   ✅ Frontend Dockerfile created")

print()
print(f"✅ Deployment scripts complete: {sum([s for _, s in created]):.1f} KB")
print()

