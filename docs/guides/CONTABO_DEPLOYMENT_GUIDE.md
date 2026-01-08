# 🚀 COMPLETE CONTABO VPS DEPLOYMENT GUIDE
## WorkingTracker.com Production Deployment

## Overview

This guide will help you deploy the complete WorkingTracker platform on your Contabo VPS with:
- **Domain:** workingtracker.com
- **OS:** Ubuntu 24.04
- **Database:** Pure PostgreSQL (no Supabase)
- **Deployment:** Docker + Docker Compose
- **SSL:** Let's Encrypt (free)

---

## 📋 Pre-Deployment Checklist

### 1. DNS Configuration (Do This First!)

Point your domain to your Contabo VPS IP address:

```
A Record:     workingtracker.com      →  YOUR_VPS_IP
A Record:     www.workingtracker.com  →  YOUR_VPS_IP
A Record:     api.workingtracker.com  →  YOUR_VPS_IP
```

**Wait 5-10 minutes for DNS propagation**

### 2. Contabo VPS Access

SSH into your server:
```bash
ssh root@YOUR_VPS_IP
```

### 3. Required Files

Make sure you have these files ready to upload:
- ✅ Complete app folder (from app.zip)
- ✅ .env.production (created above)
- ✅ postgresql_schema.sql (created above)
- ✅ docker-compose.production.yml (created above)
- ✅ nginx.production.conf (created above)
- ✅ deploy_to_contabo.sh (created above)

---

## 🎯 DEPLOYMENT STEPS

### Step 1: Upload Files to VPS

From your local machine:

```bash
# Create deployment package
cd /path/to/app
tar -czf workingtracker-deploy.tar.gz .

# Upload to VPS
scp workingtracker-deploy.tar.gz root@YOUR_VPS_IP:/root/

# SSH into VPS
ssh root@YOUR_VPS_IP
```

### Step 2: Extract Files

On the VPS:

```bash
cd /root
tar -xzf workingtracker-deploy.tar.gz
cd app
```

### Step 3: Run Automated Deployment

```bash
# Make script executable
chmod +x deploy_to_contabo.sh

# Run deployment (this will take 10-15 minutes)
./deploy_to_contabo.sh
```

The script will automatically:
- ✅ Update system packages
- ✅ Install Docker & Docker Compose
- ✅ Create application directories
- ✅ Generate security secrets
- ✅ Obtain SSL certificates
- ✅ Configure firewall
- ✅ Initialize PostgreSQL database
- ✅ Build & start all services
- ✅ Setup automated backups
- ✅ Create management scripts

### Step 4: Verify Deployment

Check if all services are running:

```bash
cd /var/www/workingtracker
docker-compose -f docker-compose.production.yml ps
```

You should see:
- ✅ postgres (healthy)
- ✅ redis (healthy)
- ✅ backend (healthy)
- ✅ frontend (running)
- ✅ nginx (running)

### Step 5: Test the Platform

Open your browser and visit:
- **Frontend:** https://workingtracker.com
- **API Docs:** https://api.workingtracker.com/docs
- **Health Check:** https://api.workingtracker.com/health

### Step 6: Create Admin User

Using the API documentation at https://api.workingtracker.com/docs:

1. Go to `/api/auth/register`
2. Click "Try it out"
3. Enter admin details:
```json
{
  "email": "admin@workingtracker.com",
  "password": "SecurePassword123!",
  "full_name": "Admin User",
  "organization_name": "WorkingTracker"
}
```
4. Execute
5. Login at https://workingtracker.com

---

## 🔧 POST-DEPLOYMENT CONFIGURATION

### 1. Update Environment Variables

Edit production environment:
```bash
cd /var/www/workingtracker
nano .env.production
```

**Update these:**
```bash
# Email Settings
SMTP_USER=your-actual-email@gmail.com
SMTP_PASSWORD=your-app-specific-password

# Database Password (CHANGE THIS!)
POSTGRES_PASSWORD=YourVeryStrongPassword123!
```

**Restart services after changes:**
```bash
./restart.sh
```

### 2. Configure Email

For Gmail:
1. Enable 2-factor authentication
2. Generate app-specific password: https://myaccount.google.com/apppasswords
3. Update SMTP_PASSWORD in .env.production

### 3. Test Stripe Integration

1. Go to https://dashboard.stripe.com
2. Test webhook: https://api.workingtracker.com/api/payments/webhook
3. Verify payments work in dashboard

---

## 🛠️ MANAGEMENT COMMANDS

Navigate to app directory:
```bash
cd /var/www/workingtracker
```

### Start Services
```bash
./start.sh
```

### Stop Services
```bash
./stop.sh
```

### Restart Services
```bash
./restart.sh
```

### View Logs
```bash
./logs.sh
```

### Check Status
```bash
./status.sh
```

### View Specific Service Logs
```bash
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f frontend
docker-compose -f docker-compose.production.yml logs -f postgres
docker-compose -f docker-compose.production.yml logs -f nginx
```

---

## 🔒 SECURITY CHECKLIST

After deployment, ensure:

- [ ] Changed database password in .env.production
- [ ] Generated unique JWT_SECRET
- [ ] Generated unique SECRET_KEY
- [ ] SSL certificates are working (https://)
- [ ] Firewall is enabled
- [ ] Email notifications are working
- [ ] Backups are running (check /var/www/workingtracker/backups)
- [ ] Logs are rotating properly
- [ ] All API keys are kept secure

---

## 💾 BACKUP & RESTORE

### Automatic Backups

Backups run automatically every day at 2 AM:
- Database backups: `/var/www/workingtracker/backups/db_*.sql.gz`
- Upload backups: `/var/www/workingtracker/backups/uploads_*.tar.gz`
- Retention: 7 days

### Manual Backup

```bash
cd /var/www/workingtracker
./backup.sh
```

### Restore from Backup

```bash
# Restore database
gunzip < backups/db_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U workingtracker_user -d workingtracker

# Restore uploads
tar -xzf backups/uploads_YYYYMMDD_HHMMSS.tar.gz -C /
```

---

## 🐛 TROUBLESHOOTING

### Issue: Services won't start

**Solution:**
```bash
cd /var/www/workingtracker
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
./logs.sh
```

### Issue: Database connection errors

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.production.yml ps postgres

# Check PostgreSQL logs
docker-compose -f docker-compose.production.yml logs postgres

# Restart PostgreSQL
docker-compose -f docker-compose.production.yml restart postgres
```

### Issue: SSL certificate errors

**Solution:**
```bash
# Renew certificates manually
certbot renew

# Copy new certificates
cp /etc/letsencrypt/live/workingtracker.com/fullchain.pem /var/www/workingtracker/nginx/ssl/
cp /etc/letsencrypt/live/workingtracker.com/privkey.pem /var/www/workingtracker/nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### Issue: Can't access website

**Check DNS:**
```bash
nslookup workingtracker.com
```

**Check if services are running:**
```bash
./status.sh
```

**Check Nginx logs:**
```bash
docker-compose -f docker-compose.production.yml logs nginx
```

**Check firewall:**
```bash
sudo ufw status
```

### Issue: API returns 500 errors

**Check backend logs:**
```bash
docker-compose -f docker-compose.production.yml logs -f backend
```

**Common fixes:**
- Verify DATABASE_URL is correct
- Check .env.production file
- Restart backend: `docker-compose -f docker-compose.production.yml restart backend`

---

## 📊 MONITORING

### Check Service Health

```bash
# Backend health
curl https://api.workingtracker.com/health

# Database health
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Redis health
docker-compose -f docker-compose.production.yml exec redis redis-cli ping
```

### Monitor Resource Usage

```bash
# Docker stats
docker stats

# Disk usage
df -h

# Memory usage
free -h

# CPU usage
top
```

### View System Logs

```bash
# All logs
cd /var/www/workingtracker/logs
tail -f *.log

# Nginx access logs
docker-compose -f docker-compose.production.yml exec nginx tail -f /var/log/nginx/access.log
```

---

## 🚀 SCALING TIPS

### Increase Performance

**1. Database Optimization:**
```bash
# Edit PostgreSQL config for better performance
docker-compose -f docker-compose.production.yml exec postgres nano /var/lib/postgresql/data/postgresql.conf

# Increase shared_buffers, effective_cache_size
```

**2. Redis Caching:**
```bash
# Already configured - verify it's being used
docker-compose -f docker-compose.production.yml logs redis
```

**3. Nginx Optimization:**
```bash
# Already configured with:
# - Gzip compression
# - Static file caching
# - Connection limits
```

### Horizontal Scaling

When you need to scale beyond one server:

1. **Database:** Move to managed PostgreSQL (Digital Ocean, AWS RDS)
2. **Redis:** Use Redis Cloud or AWS ElastiCache
3. **Backend:** Run multiple backend containers with load balancer
4. **Frontend:** Use CDN (Cloudflare, AWS CloudFront)
5. **Uploads:** Move to S3 or similar object storage

---

## 📝 MAINTENANCE TASKS

### Weekly
- [ ] Check disk space: `df -h`
- [ ] Review error logs
- [ ] Test backups

### Monthly
- [ ] Update packages: `apt update && apt upgrade`
- [ ] Review SSL certificates: `certbot certificates`
- [ ] Check for Docker image updates
- [ ] Review and optimize database

### Quarterly
- [ ] Full security audit
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Update documentation

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs:** `cd /var/www/workingtracker && ./logs.sh`
2. **Review this guide:** Follow troubleshooting steps
3. **Check service status:** `./status.sh`
4. **Search error messages:** Google the exact error
5. **Restart services:** `./restart.sh`

---

## ✅ DEPLOYMENT VERIFICATION CHECKLIST

After deployment, verify:

- [ ] https://workingtracker.com loads (frontend)
- [ ] https://api.workingtracker.com/docs loads (API docs)
- [ ] https://api.workingtracker.com/health returns 200
- [ ] Can register new user
- [ ] Can login
- [ ] Can create project
- [ ] Can start time tracking
- [ ] Screenshots are uploading
- [ ] AI insights are generating
- [ ] Stripe test payment works
- [ ] Email notifications work
- [ ] Backups are running
- [ ] SSL certificates are valid
- [ ] Firewall is active
- [ ] All services show "healthy" status

---

## 🎉 CONGRATULATIONS!

Your WorkingTracker platform is now live at:
- **https://workingtracker.com**

Start tracking time, managing teams, and growing your business! 🚀

---

## 📚 Additional Resources

- **API Documentation:** https://api.workingtracker.com/docs
- **Docker Docs:** https://docs.docker.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs
- **Let's Encrypt:** https://letsencrypt.org
- **Nginx Docs:** https://nginx.org/en/docs
