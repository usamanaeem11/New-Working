"""
AI Model Training Data Generator
Creates synthetic training data for initial model training
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

def generate_performance_training_data(num_samples: int = 1000) -> List[Dict]:
    """
    Generate synthetic performance training data
    
    Args:
        num_samples: Number of training samples to generate
        
    Returns:
        List of training records
    """
    departments = ['engineering', 'sales', 'marketing', 'hr', 'finance']
    roles = ['senior', 'junior', 'mid-level']
    
    training_data = []
    
    for i in range(num_samples):
        # Random employee metrics
        hours_per_week = random.uniform(35, 50)
        task_completion_rate = random.uniform(0.6, 1.0)
        avg_task_duration = random.uniform(1.0, 4.0)
        attendance_rate = random.uniform(0.85, 1.0)
        overtime_hours = random.uniform(0, 10)
        days_since_hire = random.randint(30, 1825)  # 1 month to 5 years
        
        department = random.choice(departments)
        role = random.choice(roles)
        
        # Calculate performance score (target variable)
        # Higher completion rate, better attendance = higher score
        base_score = 50
        base_score += task_completion_rate * 30
        base_score += (attendance_rate - 0.85) * 100
        base_score += (50 - hours_per_week) * 0.2  # Slight penalty for overwork
        base_score += (4 - avg_task_duration) * 3  # Faster tasks = better
        
        # Adjust for role
        if role == 'senior':
            base_score += 5
        elif role == 'junior':
            base_score -= 5
        
        # Add some noise
        performance_score = base_score + random.uniform(-5, 5)
        performance_score = max(0, min(100, performance_score))  # Clip to 0-100
        
        record = {
            'hours_per_week': hours_per_week,
            'task_completion_rate': task_completion_rate,
            'avg_task_duration': avg_task_duration,
            'attendance_rate': attendance_rate,
            'overtime_hours': overtime_hours,
            'days_since_hire': days_since_hire,
            'department': department,
            'role': role,
            'hire_date': datetime.now() - timedelta(days=days_since_hire),
            'performance_score': performance_score,
        }
        
        training_data.append(record)
    
    return training_data

def generate_turnover_training_data(num_samples: int = 1000) -> List[Dict]:
    """
    Generate synthetic turnover training data
    
    Args:
        num_samples: Number of training samples to generate
        
    Returns:
        List of training records
    """
    training_data = []
    
    for i in range(num_samples):
        # Random employee metrics
        tenure = random.randint(30, 1825)  # 1 month to 5 years
        satisfaction_score = random.uniform(30, 100)
        last_promotion_days = random.randint(0, 730)  # 0 to 2 years
        salary_percentile = random.uniform(20, 90)
        performance_score = random.uniform(50, 100)
        absences_per_month = random.uniform(0, 3)
        overtime_hours_per_week = random.uniform(0, 15)
        manager_quality_score = random.uniform(40, 100)
        
        # Calculate turnover probability
        # Low satisfaction, low salary, no promotions = higher turnover
        turnover_prob = 0.1  # Base 10% turnover
        
        if satisfaction_score < 50:
            turnover_prob += 0.3
        elif satisfaction_score < 70:
            turnover_prob += 0.1
        
        if salary_percentile < 40:
            turnover_prob += 0.2
        
        if last_promotion_days > 548:  # 18 months
            turnover_prob += 0.15
        
        if performance_score > 80 and salary_percentile < 50:
            turnover_prob += 0.2  # High performers leaving due to pay
        
        if manager_quality_score < 60:
            turnover_prob += 0.15
        
        # Determine if employee left
        left_within_90_days = random.random() < turnover_prob
        
        record = {
            'tenure': tenure,
            'satisfaction_score': satisfaction_score,
            'last_promotion_days': last_promotion_days,
            'salary_percentile': salary_percentile,
            'performance_score': performance_score,
            'absences_per_month': absences_per_month,
            'overtime_hours_per_week': overtime_hours_per_week,
            'manager_quality_score': manager_quality_score,
            'hire_date': datetime.now() - timedelta(days=tenure),
            'last_promotion_date': datetime.now() - timedelta(days=last_promotion_days) if last_promotion_days > 0 else None,
            'left_within_90_days': left_within_90_days,
        }
        
        training_data.append(record)
    
    return training_data

if __name__ == '__main__':
    print("Generating training data...")
    
    # Generate performance data
    perf_data = generate_performance_training_data(1000)
    print(f"Generated {len(perf_data)} performance training samples")
    
    # Generate turnover data
    turnover_data = generate_turnover_training_data(1000)
    print(f"Generated {len(turnover_data)} turnover training samples")
    
    print("Training data ready!")
