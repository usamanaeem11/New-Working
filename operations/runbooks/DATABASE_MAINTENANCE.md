# Database Maintenance Runbook

## Routine Maintenance

### Daily
- Check replication lag
- Review slow query log
- Monitor disk usage

### Weekly
- Analyze query performance
- Review index usage
- Check for bloat

### Monthly
- Full backup verification
- Capacity planning review
- Performance tuning

## Procedures

### Backup Verification
```bash
# 1. List recent backups
aws s3 ls s3://backups/postgres/

# 2. Restore to test instance
pg_restore -d test_db backup.dump

# 3. Verify data integrity
psql test_db -c "SELECT COUNT(*) FROM employees;"
```

### Index Maintenance
```sql
-- Analyze tables
ANALYZE VERBOSE employees;

-- Rebuild indexes if needed
REINDEX TABLE employees;
```

