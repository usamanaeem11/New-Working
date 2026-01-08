# Deployment Guide

## Quick Deploy (Docker)

```bash
# Clone repository
git clone <repo>
cd working-tracker

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# Access
# Web: http://localhost:3000
# API: http://localhost:8000
```

## Production Deployment

### Requirements
- Ubuntu 24.04 LTS
- Docker & Docker Compose
- SSL certificate
- Domain name

### Steps

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

2. **Clone & Configure**
```bash
git clone <repo>
cd working-tracker
cp .env.example .env
nano .env  # Configure production values
```

3. **SSL Setup**
```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d yourdomain.com
```

4. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

5. **Verify**
```bash
docker-compose ps
curl https://yourdomain.com/health
```

## Monitoring

- Logs: `docker-compose logs -f`
- Health: `curl http://localhost:8000/health`
- Metrics: Prometheus + Grafana

## Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U wos_user working_tracker > backup.sql
```
