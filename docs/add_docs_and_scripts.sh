#!/bin/bash

# Add documentation
mkdir -p docs/{api,guides,architecture}

cat > docs/API.md << 'EOF'
# Working Tracker - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.workingtracker.com
```

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Employees
- GET    /api/employees       - List all employees
- POST   /api/employees       - Create employee
- GET    /api/employees/{id}  - Get employee details
- PUT    /api/employees/{id}  - Update employee
- DELETE /api/employees/{id}  - Delete employee

### Teams
- GET    /api/teams           - List all teams
- POST   /api/teams           - Create team

### Projects  
- GET    /api/projects        - List all projects
- POST   /api/projects        - Create project

### Time Entries
- GET    /api/time-entries    - List time entries
- POST   /api/time-entries    - Create time entry

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error
EOF

cat > docs/DEPLOYMENT.md << 'EOF'
# Deployment Guide

## Quick Deploy (Docker)

1. Clone repository
2. Copy .env.example to .env
3. Fill in credentials in .env
4. Run: docker-compose up -d
5. Access: http://localhost:3000

## Manual Deploy

See COMPLETE-SETUP-GUIDE.md for detailed instructions.

## Production Deploy

1. Set ENVIRONMENT=production in .env
2. Use docker-compose.production.yml
3. Configure SSL certificates
4. Set up monitoring
5. Configure backups
EOF

cat > docs/ARCHITECTURE.md << 'EOF'
# Working Tracker - Architecture

## System Overview

```
┌─────────────────────────────────────────┐
│            Frontend (Next.js)            │
│         Port 3000                       │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│         Backend API (FastAPI)           │
│         Port 8000                       │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴────────┐
    ↓                  ↓
┌────────┐       ┌─────────┐
│Postgres│       │  Redis  │
│Port5432│       │Port 6379│
└────────┘       └─────────┘
```

## Tech Stack

- **Backend:** FastAPI (Python 3.12+)
- **Frontend:** Next.js 14 (React + TypeScript)
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Mobile:** React Native
- **Desktop:** Electron
EOF

# Add scripts
mkdir -p scripts

cat > scripts/setup.sh << 'EOF'
#!/bin/bash
echo "Setting up Working Tracker..."

# Backend
cd backend-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend
cd web-app
npm install
cd ..

echo "✅ Setup complete!"
echo "Run: docker-compose up -d"
EOF

chmod +x scripts/setup.sh

cat > scripts/test.sh << 'EOF'
#!/bin/bash
echo "Running tests..."

# Backend tests
cd backend-api
source venv/bin/activate
pytest
cd ..

# Frontend tests
cd web-app
npm test
cd ..

echo "✅ Tests complete!"
EOF

chmod +x scripts/test.sh

echo "✅ Documentation and scripts added"
