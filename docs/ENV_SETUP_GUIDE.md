# 🔐 ENVIRONMENT CONFIGURATION GUIDE

## ✅ YES - `.env` FILE IS ABSOLUTELY REQUIRED!

The `.env` file contains ALL critical configuration including:
- Database credentials
- API keys
- Security secrets
- Integration credentials
- Feature flags
- Payment gateway keys

**WITHOUT `.env`, THE APPLICATION WILL NOT RUN!**

---

## 🚀 QUICK START - 3 STEPS

### Step 1: Copy the Template
```bash
cp .env.example .env
```

### Step 2: Generate Secure Secrets
```bash
# Generate JWT secret (32+ characters)
openssl rand -base64 32

# Generate session secret (32+ characters)
openssl rand -base64 32

# Generate database password
openssl rand -base64 24
```

### Step 3: Fill Required Values
Edit `.env` and fill in at minimum:
- Database credentials
- JWT secrets
- Email configuration (for user registration)

---

## 📋 ENVIRONMENT SETUP BY USE CASE

### 🏢 MINIMAL SETUP (Local Development)

**Required Variables (25):**
```bash
# Application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:3000
API_URL=http://localhost:8000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=workingtracker_db
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT
JWT_SECRET_KEY=generated_32_char_secret_from_step2
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Gmail for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM_EMAIL=noreply@localhost
SMTP_USE_TLS=true

# Session
SESSION_SECRET=generated_32_char_secret_from_step2
```

**Time to setup:** 10 minutes
**Can start:** Immediately
**Features:** Core platform only

---

### 🎯 STANDARD SETUP (Staging/Testing)

**Required Variables (50):**
All from Minimal Setup PLUS:

```bash
# File Storage (AWS S3)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=workingtracker-test

# Payment (Test Mode)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Basic Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
GOOGLE_MAPS_API_KEY=your_maps_key

# Monitoring
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=staging
```

**Time to setup:** 30 minutes
**Can start:** After AWS/Stripe setup
**Features:** 80% of features

---

### 🏆 PRODUCTION SETUP (Full Deployment)

**Required Variables (120+):**
All from Standard Setup PLUS:

```bash
# Production URLs
APP_ENV=production
APP_DEBUG=false
APP_URL=https://workingtracker.com
API_URL=https://api.workingtracker.com

# Security
HTTPS_ENABLED=true
FORCE_HTTPS=true
CSRF_ENABLED=true

# All Integrations
JIRA_API_TOKEN=...
ASANA_ACCESS_TOKEN=...
QUICKBOOKS_CLIENT_ID=...
GITHUB_CLIENT_ID=...
TEAMS_CLIENT_ID=...
(50+ integration keys)

# Monitoring
NEW_RELIC_LICENSE_KEY=...
DATADOG_API_KEY=...

# Backups
BACKUP_ENABLED=true
BACKUP_S3_BUCKET=workingtracker-backups

# CDN
CLOUDFLARE_API_TOKEN=...
```

**Time to setup:** 2-4 hours
**Can start:** After all services configured
**Features:** 100% complete

---

## 🔑 WHERE TO GET API KEYS

### Essential Services (Required)

| Service | Purpose | Get Key From | Time |
|---------|---------|--------------|------|
| **PostgreSQL** | Database | Self-hosted or AWS RDS | 5 min |
| **Redis** | Caching | Self-hosted or Redis Labs | 5 min |
| **SMTP/Email** | User emails | Gmail App Password | 2 min |
| **AWS S3** | File storage | AWS Console | 10 min |
| **Stripe** | Payments | stripe.com/register | 5 min |

### Integration Services (Optional)

| Service | Purpose | Get Key From | Cost |
|---------|---------|--------------|------|
| **Slack** | Slack integration | api.slack.com/apps | Free |
| **Jira** | Jira integration | atlassian.com/api | Free |
| **QuickBooks** | Accounting | developer.intuit.com | Free |
| **Google Maps** | GPS tracking | console.cloud.google.com | Free tier |
| **Twilio** | SMS/WhatsApp | twilio.com | Pay-as-go |
| **Sentry** | Error tracking | sentry.io | Free tier |

### Monitoring Services (Recommended)

| Service | Purpose | Get Key From | Cost |
|---------|---------|--------------|------|
| **Sentry** | Error tracking | sentry.io | Free tier |
| **New Relic** | Performance | newrelic.com | Free tier |
| **Datadog** | Infrastructure | datadoghq.com | Free trial |

---

## 📝 ENVIRONMENT-SPECIFIC CONFIGS

### Development (.env.development)
```bash
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:3000
LOG_LEVEL=debug
RATE_LIMIT_PER_MINUTE=1000
MOCK_EXTERNAL_APIS=true
```

### Staging (.env.staging)
```bash
APP_ENV=staging
APP_DEBUG=true
APP_URL=https://staging.workingtracker.com
LOG_LEVEL=info
RATE_LIMIT_PER_MINUTE=100
MOCK_EXTERNAL_APIS=false
```

### Production (.env.production)
```bash
APP_ENV=production
APP_DEBUG=false
APP_URL=https://workingtracker.com
LOG_LEVEL=warn
RATE_LIMIT_PER_MINUTE=60
HTTPS_ENABLED=true
FORCE_HTTPS=true
```

---

## 🛡️ SECURITY BEST PRACTICES

### 1. Generate Strong Secrets
```bash
# JWT Secret (minimum 32 characters)
openssl rand -base64 32

# Session Secret (minimum 32 characters)
openssl rand -base64 32

# Database Password (minimum 16 characters)
openssl rand -base64 24

# API Keys (minimum 32 characters)
openssl rand -hex 32
```

### 2. Secure File Permissions
```bash
# Set .env to read-only for owner
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- (600)
```

### 3. Git Ignore
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore

# Verify not tracked
git status
```

### 4. Different Secrets Per Environment
```bash
# NEVER use same secrets in dev/staging/production
# Generate unique secrets for each environment
```

---

## 🐳 DOCKER ENVIRONMENT

### Using docker-compose
```yaml
# docker-compose.yml already configured to use .env
# Just create .env file and run:

docker-compose up -d
```

### Environment Variables Priority
```
1. docker-compose.yml environment section
2. .env file in project root
3. Default values in code
```

---

## ✅ VALIDATION CHECKLIST

Before running the application, verify:

### Required (Must Have)
- [ ] .env file exists
- [ ] Database credentials set
- [ ] JWT secrets generated (32+ chars)
- [ ] Redis credentials set
- [ ] Email/SMTP configured
- [ ] Session secret generated

### Recommended (Should Have)
- [ ] AWS S3 configured (file uploads)
- [ ] Stripe configured (payments)
- [ ] File permissions set (chmod 600)
- [ ] Not tracked in git

### Optional (Nice to Have)
- [ ] Slack integration
- [ ] Monitoring tools (Sentry)
- [ ] CDN configured
- [ ] All third-party integrations

---

## 🔍 TROUBLESHOOTING

### Issue: "Cannot connect to database"
```bash
# Check database credentials
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME

# Test connection
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
```

### Issue: "Invalid JWT token"
```bash
# Verify JWT secret is set
grep JWT_SECRET_KEY .env

# Must be 32+ characters
# Regenerate if needed
openssl rand -base64 32
```

### Issue: "Cannot send emails"
```bash
# For Gmail, use App Password
# Not your regular password!
# Generate at: https://myaccount.google.com/apppasswords
```

### Issue: "Redis connection failed"
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Check credentials
grep REDIS_ .env
```

---

## 📚 QUICK REFERENCE

### Generate All Secrets at Once
```bash
#!/bin/bash
echo "JWT_SECRET_KEY=$(openssl rand -base64 32)"
echo "SESSION_SECRET=$(openssl rand -base64 32)"
echo "DB_PASSWORD=$(openssl rand -base64 24)"
echo "REDIS_PASSWORD=$(openssl rand -base64 24)"
echo "INTERNAL_API_KEY=$(openssl rand -hex 32)"
echo "WEBHOOK_SIGNING_SECRET=$(openssl rand -hex 32)"
```

### Validate .env File
```bash
# Check if all required vars are set
grep -E "^(DB_|REDIS_|JWT_|SMTP_|SESSION_)" .env | wc -l
# Should be 15+ for minimal setup
```

### Backup .env Securely
```bash
# Encrypt before backing up
openssl enc -aes-256-cbc -salt -in .env -out .env.encrypted

# Decrypt when needed
openssl enc -d -aes-256-cbc -in .env.encrypted -out .env
```

---

## 🎯 RECOMMENDED SETUP PATH

### Phase 1: Local Development (Day 1)
```
1. Copy .env.example to .env
2. Set minimal 25 variables
3. Run: docker-compose up
4. Test: http://localhost:3000
```

### Phase 2: AWS Setup (Day 2)
```
1. Create AWS account
2. Set up S3 bucket
3. Generate access keys
4. Update .env with AWS credentials
```

### Phase 3: Payment Setup (Day 3)
```
1. Create Stripe account
2. Get test API keys
3. Update .env with Stripe keys
4. Test payment flow
```

### Phase 4: Integrations (Week 2)
```
1. Set up needed integrations
2. Add API keys to .env
3. Test each integration
4. Document for team
```

### Phase 5: Production (Week 3)
```
1. Get production credentials
2. Create .env.production
3. Set security settings
4. Deploy to production
5. Monitor closely
```

---

## 📞 NEED HELP?

If you're stuck:
1. Check the .env.example file for examples
2. Verify all required variables are set
3. Check logs for specific error messages
4. Test each service independently
5. Consult service-specific documentation

---

**REMEMBER:** 
- `.env` is REQUIRED - application will not run without it!
- NEVER commit `.env` to version control
- Use different secrets for dev/staging/production
- Keep backups encrypted
- Rotate secrets regularly

**YOU'RE READY TO GO!** 🚀
