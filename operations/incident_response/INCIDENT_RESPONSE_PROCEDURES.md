# Incident Response Procedures

## Phase 1: Detection & Alert (0-5 minutes)

### Automatic Detection
```yaml
Monitoring Systems:
  - Prometheus alerts
  - Application logs
  - Error tracking (Sentry)
  - Uptime monitors
  - Customer reports
```

### Manual Reporting
1. Customer reports issue via support
2. Internal team notices problem
3. Monitoring alert fires

### Initial Actions
```bash
# 1. Acknowledge the alert
pagerduty acknowledge <incident_id>

# 2. Check monitoring dashboards
open https://monitoring.workingtracker.com

# 3. Verify scope
curl https://api.workingtracker.com/health
```

---

## Phase 2: Assessment (5-15 minutes)

### Severity Assessment Checklist
```
[ ] How many customers affected?
[ ] What functionality is impacted?
[ ] Is data at risk?
[ ] Is security compromised?
[ ] What's the business impact?
```

### Severity Assignment
Use INCIDENT_CLASSIFICATION.md to assign P0-P3

### Create Incident Ticket
```bash
# Create incident in system
./scripts/create_incident.sh   --severity=P1   --title="API Gateway Timeout"   --impact="High - All API calls affected"
```

---

## Phase 3: Communication (15-30 minutes)

### Internal Communication
**Slack Channel:** `#incident-response`

**Initial Message Template:**
```
🚨 INCIDENT ALERT: [P0/P1/P2/P3]

TITLE: [Brief description]
IMPACT: [What's affected]
CUSTOMERS: [Number affected]
STATUS: Investigating
COMMANDER: @[name]

Live updates in thread ⬇️
```

### External Communication

**Status Page Update (P0/P1):**
```markdown
🔴 Investigating

We are currently investigating reports of [issue]. 
Our team is actively working on a resolution.

Last Updated: [timestamp]
```

**Customer Email (P0):**
```
Subject: [Action Required] Service Disruption

Dear WorkingTracker Customer,

We are experiencing a service disruption affecting [feature].

Status: [current status]
Impact: [what you can't do]
Workaround: [if available]
ETA: [if known]

We will provide updates every hour.
```

---

## Phase 4: Investigation (30+ minutes)

### Root Cause Analysis Steps

1. **Gather Data**
```bash
# Check application logs
kubectl logs -f deployment/api --tail=100

# Check database
psql -c "SELECT * FROM pg_stat_activity WHERE state != 'idle';"

# Check system resources
top -bn1 | head -20
df -h
```

2. **Recent Changes**
```bash
# Check recent deployments
git log --since="2 hours ago" --oneline

# Check configuration changes
./scripts/config_diff.sh production
```

3. **Reproduce Issue**
```bash
# Try to reproduce locally
curl -v https://api.workingtracker.com/endpoint
```

4. **Form Hypothesis**
- What changed?
- When did it start?
- What's the pattern?

---

## Phase 5: Mitigation (Variable)

### Quick Fixes

**Rollback Deployment:**
```bash
# Rollback to previous version
kubectl rollout undo deployment/api

# Verify rollback
kubectl rollout status deployment/api
```

**Restart Services:**
```bash
# Restart pods
kubectl rollout restart deployment/api

# Restart specific service
systemctl restart api-service
```

**Scale Resources:**
```bash
# Increase replicas
kubectl scale deployment/api --replicas=10

# Increase memory
kubectl set resources deployment/api -c=api --limits=memory=4Gi
```

**Circuit Breaker:**
```bash
# Disable problematic feature
./scripts/feature_flag.sh disable new_feature

# Enable maintenance mode
./scripts/maintenance_mode.sh enable
```

### Database Issues
```bash
# Kill long-running queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';

# Rebuild indexes
REINDEX TABLE employees;

# Vacuum database
VACUUM ANALYZE;
```

---

## Phase 6: Resolution (Variable)

### Verification Checklist
```
[ ] Primary functionality restored
[ ] Monitoring shows normal metrics
[ ] Error rates returned to baseline
[ ] Customer verification received
[ ] All systems green in status page
```

### Resolution Steps
1. Verify fix in production
2. Monitor for 30 minutes
3. Update status page: "Resolved"
4. Send customer communication
5. Close incident ticket

**Status Page Update:**
```markdown
✅ Resolved

The issue affecting [feature] has been resolved.

All systems are now operating normally.

Root Cause: [brief explanation]
Resolution: [what was done]

Resolved at: [timestamp]
```

---

## Phase 7: Post-Mortem (24-48 hours)

### Post-Mortem Template
```markdown
# Incident Post-Mortem

**Incident:** [ID and Title]
**Date:** [Date]
**Duration:** [Start - End time]
**Severity:** P0/P1/P2
**Impact:** [Customer count and business impact]

## Timeline
- [Time] - Incident detected
- [Time] - Team assembled
- [Time] - Root cause identified
- [Time] - Fix deployed
- [Time] - Incident resolved

## Root Cause
[Detailed explanation]

## Resolution
[What was done to fix]

## Impact
- Customers affected: [count]
- Revenue impact: [$amount]
- Duration: [time]

## What Went Well
- [Positive aspects]

## What Went Wrong
- [Issues in response]

## Action Items
1. [Preventive measure] - Owner: [name] - Due: [date]
2. [Monitoring improvement] - Owner: [name] - Due: [date]
3. [Process change] - Owner: [name] - Due: [date]

## Follow-up
Next review: [date]
```

---

## Incident Commander Responsibilities

### During Incident
- [ ] Assess severity
- [ ] Assemble response team
- [ ] Coordinate investigation
- [ ] Make critical decisions
- [ ] Communicate with stakeholders
- [ ] Update status page
- [ ] Track actions and timeline

### After Resolution
- [ ] Verify resolution
- [ ] Send customer communication
- [ ] Schedule post-mortem
- [ ] Ensure action items assigned
- [ ] Update runbooks

---

## Contact Information

### Escalation Chain
1. **On-Call Engineer** - PagerDuty
2. **Engineering Manager** - [phone]
3. **VP Engineering** - [phone]
4. **CTO** - [phone]
5. **CEO** - [phone]

### Key Contacts
- **Security Team:** security@workingtracker.com
- **Customer Success:** support@workingtracker.com
- **Status Page:** status.workingtracker.com
- **Incident Log:** incidents.workingtracker.com

---

## Tools & Resources

### Monitoring
- **Prometheus:** https://prometheus.workingtracker.com
- **Grafana:** https://grafana.workingtracker.com
- **Logs:** https://logs.workingtracker.com

### Communication
- **Slack:** #incident-response
- **PagerDuty:** https://workingtracker.pagerduty.com
- **Status Page:** https://status.workingtracker.com

### Documentation
- **Runbooks:** /operations/runbooks/
- **Architecture:** /docs/architecture/
- **Playbooks:** /operations/playbooks/
