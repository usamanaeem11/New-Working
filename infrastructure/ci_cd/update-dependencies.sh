#!/bin/bash
# Update all dependencies safely

set -e

echo "📦 Updating dependencies..."

# Backend
echo "🐍 Updating Python dependencies..."
cd backend-api
pip-review --auto

# Frontend
echo "⚛️ Updating Web App dependencies..."
cd ../web-app
npx npm-check-updates -u
npm install

# Mobile
echo "📱 Updating Mobile App dependencies..."
cd ../mobile-apps
npx npm-check-updates -u
npm install

# Desktop
echo "💻 Updating Desktop App dependencies..."
cd ../desktop-app
npx npm-check-updates -u
npm install

echo "✅ All dependencies updated!"
echo "Run tests to verify everything still works."
