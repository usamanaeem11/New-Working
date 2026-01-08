# 🪟 WINDOWS/WSL DEPLOYMENT GUIDE
## WorkingTracker - Complete Setup for Windows Users

---

## 📋 PREREQUISITES

### 1. Install WSL 2 (Windows Subsystem for Linux)
```powershell
# Open PowerShell as Administrator
wsl --install

# Or install specific distribution
wsl --install -d Ubuntu-22.04

# Set WSL 2 as default
wsl --set-default-version 2

# Restart your computer
```

### 2. Install Ubuntu in WSL
```powershell
# After restart, open PowerShell
wsl --list --online
wsl --install -d Ubuntu-22.04

# Launch Ubuntu
ubuntu

# Create username and password when prompted
```

### 3. Update Ubuntu
```bash
# Inside WSL Ubuntu terminal
sudo apt update && sudo apt upgrade -y
```

---

## 🐳 INSTALL DOCKER

### Option A: Docker Desktop (Recommended for Windows)
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop
3. Open Docker Desktop
4. Go to Settings → Resources → WSL Integration
5. Enable integration with your Ubuntu distribution
6. Click "Apply & Restart"

### Option B: Docker Engine in WSL (Alternative)
```bash
# Inside WSL Ubuntu
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### Verify Docker Installation
```bash
docker --version
docker-compose --version
docker ps
```

---

## 📦 DEPLOY WORKINGTRACKER

### Step 1: Transfer Files to WSL
```bash
# Option A: Copy from Windows to WSL
# In Windows, download workingtracker-PRODUCTION-FINAL.tar.gz to Downloads folder
# Then in WSL:
cd ~
cp /mnt/c/Users/YOUR_USERNAME/Downloads/workingtracker-PRODUCTION-FINAL.tar.gz .

# Option B: Download directly in WSL
cd ~
# Upload file somewhere accessible and wget it
```

### Step 2: Extract Package
```bash
cd ~
tar -xzf workingtracker-PRODUCTION-FINAL.tar.gz
cd workingtracker-PRODUCTION-FINAL
ls -la
```

### Step 3: Configure Environment
```bash
# Create .env file
cat > .env << 'ENVEOF'
# Database Configuration
POSTGRES_DB=workingtracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SecurePassword123!

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-change-this-in-production
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_PORT=8000
FRONTEND_PORT=3000
ENVEOF

echo "✅ Environment configured"
```

### Step 4: Build Docker Images
```bash
# Build all containers
docker-compose build

# This will:
# - Build backend (Python/FastAPI)
# - Build frontend (React)
# - Pull PostgreSQL image
```

**If you get CRACO errors, the package.json has been fixed!**

### Step 5: Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Initialize Database
```bash
# Wait for PostgreSQL to be ready (about 30 seconds)
sleep 30

# Database is auto-initialized with postgresql_schema.sql

# Verify database
docker-compose exec postgres psql -U postgres -d workingtracker -c "\dt"
```

### Step 7: Access Application
```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## 🔧 TROUBLESHOOTING

### Problem 1: "craco: not found"
**Solution:** Already fixed in package.json!
```bash
# If you still see this, verify package.json:
cat frontend/package.json | grep scripts
# Should show "react-scripts" not "craco"
```

### Problem 2: Docker daemon not running
```bash
# If using Docker Desktop
# - Open Docker Desktop
# - Wait for it to start
# - Ensure WSL integration is enabled

# If using Docker Engine
sudo service docker start
sudo service docker status
```

### Problem 3: Permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
# Or restart WSL
```

### Problem 4: Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Stop the service or change ports in docker-compose.yml
```

### Problem 5: Build fails with network errors
```bash
# Restart Docker
docker-compose down
sudo service docker restart
docker-compose build --no-cache
```

### Problem 6: WSL runs out of memory
```powershell
# In Windows, create/edit: C:\Users\YOUR_USERNAME\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB

# Restart WSL
wsl --shutdown
wsl
```

### Problem 7: Line ending issues (CRLF vs LF)
```bash
# Convert all Python files
find . -name "*.py" -exec dos2unix {} \;

# Or install dos2unix first
sudo apt-get install dos2unix
```

---

## 📝 USEFUL COMMANDS

### Docker Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Rebuild specific service
docker-compose up -d --build backend

# Enter container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d workingtracker

# Remove all containers and volumes
docker-compose down -v

# Check resource usage
docker stats
```

### Development Commands
```bash
# Watch backend logs
docker-compose logs -f backend

# Run backend migrations
docker-compose exec backend python -c "from db import *; # migration code"

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d workingtracker

# Backup database
docker-compose exec postgres pg_dump -U postgres workingtracker > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres workingtracker < backup.sql
```

---

## 🚀 QUICK START SCRIPT

Save this as `start.sh`:
```bash
#!/bin/bash

echo "🚀 Starting WorkingTracker..."

# Start Docker if not running
if ! docker info > /dev/null 2>&1; then
    echo "Starting Docker..."
    sudo service docker start
    sleep 5
fi

# Start services
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Check status
docker-compose ps

echo ""
echo "✅ WorkingTracker is running!"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop:      docker-compose down"
```

Make it executable:
```bash
chmod +x start.sh
./start.sh
```

---

## 📱 ACCESSING FROM WINDOWS

Your WSL services are accessible from Windows at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

You can use:
- Chrome/Edge browser
- Postman for API testing
- VS Code with Remote-WSL extension

---

## 🔒 PRODUCTION DEPLOYMENT

For production on Windows Server:
1. Use Docker Desktop with Windows Containers
2. Or deploy to Linux VPS (recommended)
3. Follow the Contabo deployment guide for Linux servers

---

## ✅ VERIFICATION CHECKLIST

- [ ] WSL 2 installed
- [ ] Ubuntu installed in WSL
- [ ] Docker installed and running
- [ ] Package files extracted
- [ ] .env file configured
- [ ] Docker images built successfully
- [ ] Services running (docker-compose ps)
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000
- [ ] Database initialized

---

## 🆘 GETTING HELP

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify Docker: `docker ps`
3. Check WSL: `wsl --list --verbose`
4. Restart Docker: `sudo service docker restart`
5. Rebuild: `docker-compose build --no-cache`

---

## 🎉 SUCCESS!

Once running, you should see:
```
✅ Backend running on port 8000
✅ Frontend running on port 3000
✅ PostgreSQL running on port 5432
```

**Visit http://localhost:3000 to start using WorkingTracker!** 🚀
