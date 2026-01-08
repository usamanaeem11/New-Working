"""
Data Seeding Script
Creates sample data for development and testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import random

from app.database.session import SessionLocal
# Import models here when available

def seed_tenants(db):
    """Seed sample tenants"""
    tenants = [
        {"name": "Acme Corporation", "domain": "acme.com"},
        {"name": "TechStart Inc", "domain": "techstart.com"},
    ]
    
    print(f"Seeding {len(tenants)} tenants...")
    # Create tenants in database
    return tenants

def seed_users(db, tenant_id):
    """Seed sample users"""
    users = [
        {
            "email": "admin@example.com",
            "password_hash": "hashed_password",  # Use bcrypt in real implementation
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "tenant_id": tenant_id
        },
        {
            "email": "manager@example.com",
            "password_hash": "hashed_password",
            "first_name": "Manager",
            "last_name": "User",
            "role": "manager",
            "tenant_id": tenant_id
        },
    ]
    
    print(f"Seeding {len(users)} users...")
    return users

def seed_employees(db, tenant_id, count=50):
    """Seed sample employees"""
    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance"]
    positions = ["Developer", "Designer", "Manager", "Analyst", "Specialist"]
    
    employees = []
    for i in range(count):
        employee = {
            "employee_number": f"EMP{str(i+1).zfill(4)}",
            "first_name": f"Employee{i+1}",
            "last_name": f"Last{i+1}",
            "email": f"employee{i+1}@example.com",
            "department": random.choice(departments),
            "position": random.choice(positions),
            "hire_date": datetime.now() - timedelta(days=random.randint(30, 730)),
            "status": "active",
            "tenant_id": tenant_id
        }
        employees.append(employee)
    
    print(f"Seeding {count} employees...")
    return employees

def seed_time_entries(db, employee_ids, days=30):
    """Seed sample time entries"""
    entries = []
    
    for employee_id in employee_ids:
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            
            # Random work hours (7-9 hours)
            hours = random.uniform(7, 9)
            
            entry = {
                "employee_id": employee_id,
                "date": date.date(),
                "clock_in": date.replace(hour=9, minute=0),
                "clock_out": date.replace(hour=int(9+hours), minute=int((hours%1)*60)),
                "hours": hours,
                "status": "approved"
            }
            entries.append(entry)
    
    print(f"Seeding {len(entries)} time entries...")
    return entries

def seed_all():
    """Seed all sample data"""
    db = SessionLocal()
    
    try:
        print("Starting data seeding...")
        
        # Seed tenants
        tenants = seed_tenants(db)
        
        for tenant in tenants[:1]:  # Just first tenant for now
            tenant_id = tenant.get('id', 1)
            
            # Seed users
            users = seed_users(db, tenant_id)
            
            # Seed employees
            employees = seed_employees(db, tenant_id, count=50)
            employee_ids = [e.get('id', i+1) for i, e in enumerate(employees)]
            
            # Seed time entries
            time_entries = seed_time_entries(db, employee_ids, days=30)
        
        db.commit()
        print("Data seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
