# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.workingtracker.com
```

## Authentication

All endpoints require JWT Bearer token:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication
- POST `/api/v1/auth/login` - User login
- POST `/api/v1/auth/register` - User registration
- POST `/api/v1/auth/logout` - User logout

### Employees
- GET `/api/v1/employees` - List employees
- POST `/api/v1/employees` - Create employee
- GET `/api/v1/employees/{id}` - Get employee
- PUT `/api/v1/employees/{id}` - Update employee
- DELETE `/api/v1/employees/{id}` - Delete employee

### Teams
- GET `/api/v1/teams` - List teams
- POST `/api/v1/teams` - Create team

### Projects
- GET `/api/v1/projects` - List projects
- POST `/api/v1/projects` - Create project

### Time Tracking
- GET `/api/v1/time-entries` - List time entries
- POST `/api/v1/time-entries` - Create time entry

## Response Format

```json
{
  "data": {},
  "message": "Success",
  "status": 200
}
```

## Error Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error
