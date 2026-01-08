#!/bin/bash
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
