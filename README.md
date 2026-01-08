# Working Tracker
> Enterprise Workforce Intelligence Platform - Complete Monorepo

[![License](https://img.shields.io/badge/license-Commercial-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](CHANGELOG.md)

## 🎯 Overview

Complete enterprise workforce management system with AI intelligence across all platforms.

## 📦 Repository Structure

```
workingtracker/
├── apps/                      Platform Applications
│   ├── web/                  Next.js Web Application
│   ├── mobile/               React Native Mobile (iOS + Android)
│   ├── desktop/              Electron Desktop (Win/Mac/Linux)
│   └── extension/            Browser Extension (Chrome/Firefox/Edge)
├── services/                  Backend Services
│   └── api/                  FastAPI Backend + 14 AI Engines
├── packages/                  Shared Libraries
│   ├── ui/                   Shared UI Components
│   ├── utils/                Shared Utilities
│   ├── types/                Shared TypeScript Types
│   └── config/               Shared Configuration
├── infrastructure/            DevOps & Infrastructure
│   ├── docker/               Docker Configurations
│   ├── kubernetes/           K8s Manifests
│   └── terraform/            Infrastructure as Code
├── database/                  Database Layer
│   ├── schemas/              Table Definitions
│   ├── migrations/           Database Migrations
│   └── seeds/                Seed Data
└── docs/                      Documentation
    ├── api/                  API Documentation
    ├── guides/               User & Developer Guides
    └── architecture/         Architecture Diagrams
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### One Command Startup

```bash
# Clone repository
git clone <repository-url>
cd workingtracker

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Start everything
docker-compose up -d

# Access applications
Web:       http://localhost:3000
API:       http://localhost:8000
API Docs:  http://localhost:8000/api/docs
Mobile:    Use Expo Go app (scan QR from terminal)
Desktop:   npm run desktop:dev
```

## 📱 Platform Development

### Web Application
```bash
cd apps/web
npm install
npm run dev
```

### Mobile Application
```bash
cd apps/mobile
npm install
npm run ios        # iOS simulator
npm run android    # Android emulator
```

### Desktop Application
```bash
cd apps/desktop
npm install
npm run dev        # Development mode
npm run build      # Production build
```

### Browser Extension
```bash
cd apps/extension
npm install
npm run dev        # Development build
npm run build      # Production build
```

### Backend API
```bash
cd services/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Platform-specific tests
npm run test:web
npm run test:mobile
npm run test:api
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Developer Guide](docs/guides/DEVELOPER.md)
- [Deployment Guide](docs/guides/DEPLOYMENT.md)

## 🔐 Security

- JWT Authentication
- OAuth 2.0 Support
- RBAC Authorization
- End-to-end Encryption
- SOC 2, GDPR, CCPA Compliant

## 🤖 AI Features

- 14 AI Intelligence Engines
- Predictive Analytics
- Automated Insights
- ML-powered Recommendations

## 📄 License

Copyright © 2026 Working Tracker. All rights reserved.
Commercial License - See [LICENSE](LICENSE) for details.

## 🤝 Support

- Website: https://workingtracker.com
- Email: support@workingtracker.com
- Documentation: https://docs.workingtracker.com
