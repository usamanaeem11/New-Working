# Incident Classification Guide

## Severity Definitions

### P0 - Critical (Emergency)
**Response Time:** Immediate (15 minutes)  
**Definition:** Complete system outage or security breach

**Examples:**
- Total system unavailable
- Data breach detected
- Payment processing failure
- Database corruption
- Authentication system down

**Response Team:**
- Incident Commander
- Engineering Lead
- Security Lead
- Customer Success Director
- CEO (notified)

**Communication:**
- Status page updated immediately
- All customers notified within 30 minutes
- Hourly updates until resolved

---

### P1 - High (Urgent)
**Response Time:** 1 hour  
**Definition:** Major feature unavailable, significant customer impact

**Examples:**
- Key feature not working
- Performance degradation (>50% slower)
- API endpoints failing
- Report generation broken
- Mobile app crashes

**Response Team:**
- On-call engineer
- Engineering manager
- Product manager

**Communication:**
- Status page updated within 1 hour
- Affected customers notified
- Updates every 4 hours

---

### P2 - Medium (Important)
**Response Time:** 4 hours (business hours)  
**Definition:** Minor feature issues, workaround available

**Examples:**
- UI display issues
- Non-critical features broken
- Performance issues (<50% impact)
- Minor data inconsistencies

**Response Team:**
- Assigned engineer
- Team lead

**Communication:**
- Internal tracking only
- Customer notification if widespread

---

### P3 - Low (Normal)
**Response Time:** 24-48 hours  
**Definition:** Cosmetic issues, feature requests

**Examples:**
- Typos
- Minor UI improvements
- Feature enhancements
- Documentation updates

**Response Team:**
- Product backlog
- Scheduled maintenance

**Communication:**
- Release notes

---

## Escalation Path

```
P3 Issue Detected
    ↓
P3 → Engineer Assigned → Fix in Sprint
    ↓
If Customer Impact Grows
    ↓
P2 → Team Lead Notified → Fix This Week
    ↓
If Multiple Customers Affected
    ↓
P1 → Manager + On-Call → Fix Today
    ↓
If System-Wide Impact
    ↓
P0 → All Hands → Fix Now
```

## De-escalation Criteria

### P0 → P1
- Primary functionality restored
- Security threat contained
- Workaround available

### P1 → P2
- Feature partially working
- <10 customers affected
- Workaround documented

### P2 → P3
- Limited scope
- Cosmetic only
- No business impact
