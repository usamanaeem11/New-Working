# Testing Framework

## Test Coverage Goals
- Unit Tests: >80%
- Integration Tests: >70%
- E2E Tests: Critical paths covered
- Load Tests: All major endpoints
- Security Tests: OWASP Top 10

## Running Tests
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# E2E tests
pytest tests/e2e -v

# Load tests
locust -f tests/load/locustfile.py

# Security tests
pytest tests/security -v
```

## Test Reports
Reports generated in: `tests/reports/`

