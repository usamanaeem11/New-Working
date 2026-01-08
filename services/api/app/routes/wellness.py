"""
Employee Wellness & Mental Health
Mood tracking, stress monitoring, wellness goals, and mental health support
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/api/wellness", tags=["Employee Wellness"])
logger = logging.getLogger(__name__)

# ============================================================
# MODELS
# ============================================================

class WellnessCheckin(BaseModel):
    employee_id: str
    mood: int  # 1-5 scale
    stress_level: int  # 1-5 scale
    energy_level: int  # 1-5 scale
    sleep_hours: Optional[float] = None
    notes: Optional[str] = None

class WellnessGoal(BaseModel):
    goal_id: Optional[str] = None
    employee_id: str
    goal_type: str  # 'exercise', 'meditation', 'breaks', 'sleep', 'hydration'
    target_value: float
    frequency: str  # 'daily', 'weekly'
    start_date: date
    end_date: date

# ============================================================
# WELLNESS CHECK-INS
# ============================================================

@router.post("/checkins")
async def submit_checkin(checkin: WellnessCheckin):
    """Submit daily wellness check-in"""
    
    logger.info(f"Wellness check-in for employee {checkin.employee_id}")
    
    checkin_id = f"wc_{hash(checkin.employee_id + str(datetime.now()))}"[:16]
    
    # Validate ranges
    if not (1 <= checkin.mood <= 5):
        raise HTTPException(status_code=400, detail="Mood must be between 1-5")
    if not (1 <= checkin.stress_level <= 5):
        raise HTTPException(status_code=400, detail="Stress level must be between 1-5")
    if not (1 <= checkin.energy_level <= 5):
        raise HTTPException(status_code=400, detail="Energy level must be between 1-5")
    
    # TODO: Insert into database
    # INSERT INTO wellness_checkins (checkin_id, employee_id, mood, stress_level, ...)
    
    # Check if stress indicators should be triggered
    if checkin.stress_level >= 4:
        logger.warning(f"High stress detected for employee {checkin.employee_id}")
        # TODO: Trigger stress alert
    
    return {
        "checkin_id": checkin_id,
        "employee_id": checkin.employee_id,
        "mood": checkin.mood,
        "stress_level": checkin.stress_level,
        "checkin_timestamp": datetime.now().isoformat(),
        "recommendation": get_recommendation(checkin)
    }

@router.get("/checkins")
async def get_checkins(
    employee_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get wellness check-in history"""
    
    # TODO: Query database
    # SELECT * FROM wellness_checkins
    # WHERE employee_id = %s
    # AND checkin_timestamp BETWEEN %s AND %s
    # ORDER BY checkin_timestamp DESC
    
    return {
        "employee_id": employee_id,
        "checkins": [
            {
                "checkin_id": "wc_1",
                "mood": 4,
                "stress_level": 2,
                "energy_level": 4,
                "sleep_hours": 7.5,
                "checkin_timestamp": "2024-01-05T09:00:00"
            },
            {
                "checkin_id": "wc_2",
                "mood": 3,
                "stress_level": 4,
                "energy_level": 2,
                "sleep_hours": 5.5,
                "checkin_timestamp": "2024-01-04T09:00:00"
            }
        ],
        "total": 2
    }

@router.get("/checkins/trends")
async def get_wellness_trends(
    employee_id: str,
    period: str = "30days"  # 7days, 30days, 90days, 1year
):
    """Get wellness trends over time"""
    
    # TODO: Calculate averages and trends from database
    
    return {
        "employee_id": employee_id,
        "period": period,
        "averages": {
            "mood": 3.8,
            "stress_level": 2.5,
            "energy_level": 3.9,
            "sleep_hours": 7.2
        },
        "trend": {
            "mood": "improving",  # improving, declining, stable
            "stress": "stable",
            "energy": "improving"
        },
        "weekly_breakdown": [
            {
                "week": "2024-W1",
                "avg_mood": 4.2,
                "avg_stress": 2.1,
                "avg_energy": 4.1
            }
        ],
        "insights": [
            "Your mood has improved 15% over the last month",
            "Stress levels are within healthy range",
            "Consider maintaining current sleep patterns"
        ]
    }

# ============================================================
# STRESS MONITORING
# ============================================================

@router.post("/stress/indicators")
async def log_stress_indicator(
    employee_id: str,
    indicator_type: str,
    metric_value: float
):
    """Log automatic stress indicator"""
    
    # Indicator types:
    # - overtime_hours
    # - missed_breaks
    # - after_hours_work
    # - rapid_activity
    # - long_sessions
    
    logger.info(f"Stress indicator: {indicator_type} = {metric_value} for {employee_id}")
    
    indicator_id = f"si_{hash(employee_id + indicator_type + str(datetime.now()))}"[:16]
    
    # Determine if threshold exceeded
    thresholds = {
        "overtime_hours": 10,  # >10 hours/week
        "missed_breaks": 3,  # >3 breaks/week
        "after_hours_work": 5,  # >5 hours/week
        "rapid_activity": 200,  # >200 actions/hour
        "long_sessions": 4  # >4 hours without break
    }
    
    threshold_exceeded = metric_value > thresholds.get(indicator_type, float('inf'))
    
    # TODO: Insert into database
    # INSERT INTO stress_indicators (indicator_id, employee_id, indicator_type, metric_value, threshold_exceeded)
    
    if threshold_exceeded:
        # TODO: Trigger alert to manager and HR
        logger.warning(f"Stress threshold exceeded: {indicator_type} for {employee_id}")
    
    return {
        "indicator_id": indicator_id,
        "indicator_type": indicator_type,
        "metric_value": metric_value,
        "threshold_exceeded": threshold_exceeded,
        "detected_at": datetime.now().isoformat()
    }

@router.get("/stress/analysis")
async def get_stress_analysis(employee_id: str, days: int = 30):
    """Get comprehensive stress analysis"""
    
    # TODO: Analyze all stress indicators over period
    
    return {
        "employee_id": employee_id,
        "analysis_period_days": days,
        "overall_stress_score": 6.5,  # 0-10 scale
        "stress_level": "moderate",  # low, moderate, high, critical
        "indicators_detected": [
            {
                "type": "overtime_hours",
                "frequency": 12,
                "avg_value": 12.5,
                "severity": "medium"
            },
            {
                "type": "missed_breaks",
                "frequency": 8,
                "avg_value": 4.2,
                "severity": "low"
            }
        ],
        "burnout_risk": "medium",  # low, medium, high
        "recommendations": [
            "Consider reducing overtime hours",
            "Take regular breaks throughout the day",
            "Speak with your manager about workload"
        ],
        "manager_notified": False,
        "hr_notified": False
    }

@router.get("/stress/alerts")
async def get_stress_alerts(manager_id: str):
    """Get stress alerts for team members (manager view)"""
    
    # TODO: Get employees reporting to this manager with high stress
    
    return {
        "manager_id": manager_id,
        "alerts": [
            {
                "employee_id": "emp_1",
                "employee_name": "John Doe",
                "stress_score": 8.5,
                "risk_level": "high",
                "indicators": ["overtime", "missed_breaks"],
                "days_at_risk": 14,
                "requires_action": True
            }
        ],
        "total_alerts": 1
    }

# ============================================================
# WELLNESS GOALS & CHALLENGES
# ============================================================

@router.post("/goals")
async def create_wellness_goal(goal: WellnessGoal):
    """Create a wellness goal"""
    
    goal_id = f"wg_{hash(goal.employee_id + goal.goal_type)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO wellness_goals (goal_id, employee_id, goal_type, target_value, ...)
    
    return {
        "goal_id": goal_id,
        "employee_id": goal.employee_id,
        "goal_type": goal.goal_type,
        "target_value": goal.target_value,
        "frequency": goal.frequency,
        "start_date": goal.start_date.isoformat(),
        "end_date": goal.end_date.isoformat(),
        "status": "active"
    }

@router.get("/goals")
async def get_wellness_goals(employee_id: str, status: Optional[str] = None):
    """Get employee's wellness goals"""
    
    return {
        "employee_id": employee_id,
        "goals": [
            {
                "goal_id": "wg_1",
                "goal_type": "exercise",
                "target_value": 30,  # minutes per day
                "current_progress": 22,
                "progress_percentage": 73.3,
                "frequency": "daily",
                "status": "active",
                "streak_days": 5
            },
            {
                "goal_id": "wg_2",
                "goal_type": "breaks",
                "target_value": 4,  # breaks per day
                "current_progress": 3,
                "progress_percentage": 75.0,
                "frequency": "daily",
                "status": "active",
                "streak_days": 12
            }
        ]
    }

@router.put("/goals/{goal_id}/progress")
async def update_goal_progress(goal_id: str, progress: float):
    """Update progress on a wellness goal"""
    
    # TODO: Update database
    # UPDATE wellness_goals SET current_progress = %s WHERE goal_id = %s
    
    # Check if goal completed
    # TODO: Get target_value from database
    target_value = 30
    is_completed = progress >= target_value
    
    return {
        "goal_id": goal_id,
        "current_progress": progress,
        "target_value": target_value,
        "progress_percentage": (progress / target_value) * 100,
        "is_completed": is_completed,
        "updated_at": datetime.now().isoformat()
    }

@router.get("/challenges")
async def get_team_challenges():
    """Get team wellness challenges"""
    
    return {
        "active_challenges": [
            {
                "challenge_id": "ch_1",
                "name": "January Step Challenge",
                "type": "steps",
                "goal": 10000,  # steps per day
                "duration_days": 31,
                "participants": 24,
                "leaderboard": [
                    {"employee_name": "Alice", "value": 12500, "rank": 1},
                    {"employee_name": "Bob", "value": 11200, "rank": 2}
                ]
            }
        ]
    }

# ============================================================
# WELLNESS RESOURCES
# ============================================================

@router.get("/resources")
async def get_wellness_resources(category: Optional[str] = None):
    """Get wellness resources and materials"""
    
    # TODO: Query database
    # SELECT * FROM wellness_resources
    # WHERE category = %s OR %s IS NULL
    
    return {
        "resources": [
            {
                "resource_id": "res_1",
                "title": "Mindfulness Meditation Guide",
                "category": "mental_health",
                "resource_type": "article",
                "url": "https://example.com/meditation-guide",
                "description": "A beginner's guide to mindfulness meditation"
            },
            {
                "resource_id": "res_2",
                "title": "Desk Exercises for Office Workers",
                "category": "exercise",
                "resource_type": "video",
                "url": "https://example.com/desk-exercises",
                "description": "Simple exercises you can do at your desk"
            },
            {
                "resource_id": "res_3",
                "title": "EAP - Employee Assistance Program",
                "category": "mental_health",
                "resource_type": "tool",
                "url": "https://eap.example.com",
                "description": "Confidential counseling and support services"
            }
        ],
        "categories": [
            "mental_health",
            "exercise",
            "nutrition",
            "sleep",
            "stress_management"
        ]
    }

# ============================================================
# BREAK REMINDERS
# ============================================================

@router.post("/reminders/schedule")
async def schedule_break_reminders(
    employee_id: str,
    interval_minutes: int = 60,
    enabled: bool = True
):
    """Schedule automatic break reminders"""
    
    return {
        "employee_id": employee_id,
        "interval_minutes": interval_minutes,
        "enabled": enabled,
        "next_reminder": (datetime.now() + timedelta(minutes=interval_minutes)).isoformat()
    }

@router.get("/reminders/suggestions")
async def get_break_suggestions(employee_id: str):
    """Get intelligent break suggestions based on activity"""
    
    # TODO: Analyze activity patterns
    # - Long continuous sessions
    # - High intensity periods
    # - Productivity decline indicators
    
    return {
        "employee_id": employee_id,
        "suggestions": [
            {
                "type": "stretch_break",
                "reason": "Continuous work for 2 hours",
                "duration_minutes": 5,
                "priority": "high"
            },
            {
                "type": "walk_break",
                "reason": "High screen time today",
                "duration_minutes": 10,
                "priority": "medium"
            }
        ]
    }

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_recommendation(checkin: WellnessCheckin) -> str:
    """Get personalized recommendation based on check-in"""
    
    if checkin.stress_level >= 4:
        return "Your stress level is high. Consider taking a short break or speaking with your manager."
    elif checkin.mood <= 2:
        return "We noticed you're feeling down. Remember our Employee Assistance Program is available 24/7."
    elif checkin.energy_level <= 2:
        if checkin.sleep_hours and checkin.sleep_hours < 6:
            return "Low sleep detected. Try to get 7-8 hours of sleep tonight."
        else:
            return "Energy is low. Consider a short walk or some light exercise."
    else:
        return "You're doing great! Keep up the good work."

logger.info("Wellness routes loaded")
