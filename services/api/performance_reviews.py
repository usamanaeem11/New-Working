"""
Performance Reviews & OKRs
Goal setting, performance reviews, 360 feedback, and OKR management
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/api/performance", tags=["Performance Reviews"])
logger = logging.getLogger(__name__)

# ============================================================
# MODELS
# ============================================================

class OKR(BaseModel):
    okr_id: Optional[str] = None
    organization_id: Optional[str] = None
    team_id: Optional[str] = None
    owner_id: str
    objective: str
    key_results: List[Dict[str, Any]]  # [{description, target, current, unit}]
    quarter: str  # e.g., "2024-Q1"
    year: int
    parent_okr_id: Optional[str] = None

class Goal(BaseModel):
    goal_id: Optional[str] = None
    employee_id: str
    manager_id: str
    goal_type: str  # 'performance', 'development', 'behavioral'
    description: str
    success_criteria: str
    target_date: date
    progress_percentage: float = 0

class ReviewCycle(BaseModel):
    cycle_id: Optional[str] = None
    name: str
    cycle_type: str  # 'annual', 'quarterly', 'probation'
    start_date: date
    end_date: date
    status: str = "planned"

class PerformanceReview(BaseModel):
    review_id: Optional[str] = None
    cycle_id: str
    employee_id: str
    reviewer_id: str
    review_type: str  # 'self', 'manager', 'peer', '360'
    overall_rating: Optional[int] = None  # 1-5
    competency_ratings: Optional[Dict[str, int]] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    goals_for_next_period: Optional[str] = None
    status: str = "draft"

# ============================================================
# OKR MANAGEMENT
# ============================================================

@router.post("/okrs")
async def create_okr(okr: OKR):
    """Create a new OKR"""
    
    logger.info(f"Creating OKR: {okr.objective}")
    
    okr_id = f"okr_{hash(okr.objective + okr.owner_id)}"[:16]
    
    # Validate key results
    if not okr.key_results or len(okr.key_results) < 1:
        raise HTTPException(status_code=400, detail="At least one key result is required")
    
    if len(okr.key_results) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 key results per objective")
    
    # TODO: Insert into database
    # INSERT INTO okrs (okr_id, owner_id, objective, key_results, quarter, year, ...)
    
    return {
        "okr_id": okr_id,
        "objective": okr.objective,
        "key_results_count": len(okr.key_results),
        "quarter": okr.quarter,
        "created_at": datetime.now().isoformat()
    }

@router.get("/okrs")
async def list_okrs(
    owner_id: Optional[str] = None,
    team_id: Optional[str] = None,
    quarter: Optional[str] = None,
    year: Optional[int] = None
):
    """List OKRs with filters"""
    
    # TODO: Query database
    # SELECT * FROM okrs
    # WHERE owner_id = %s OR %s IS NULL
    # AND team_id = %s OR %s IS NULL
    # AND quarter = %s OR %s IS NULL
    
    return {
        "okrs": [
            {
                "okr_id": "okr_1",
                "objective": "Increase product adoption by 50%",
                "owner_id": "user_1",
                "owner_name": "John Doe",
                "quarter": "2024-Q1",
                "progress_percentage": 65.0,
                "status": "on_track",
                "key_results": [
                    {
                        "description": "Acquire 500 new users",
                        "target": 500,
                        "current": 325,
                        "unit": "users",
                        "progress": 65.0
                    }
                ]
            }
        ],
        "total": 1
    }

@router.get("/okrs/{okr_id}")
async def get_okr(okr_id: str):
    """Get detailed OKR information"""
    
    return {
        "okr_id": okr_id,
        "objective": "Increase product adoption by 50%",
        "owner_id": "user_1",
        "owner_name": "John Doe",
        "team_id": "team_product",
        "quarter": "2024-Q1",
        "year": 2024,
        "parent_okr_id": None,
        "progress_percentage": 65.0,
        "status": "on_track",  # on_track, at_risk, off_track
        "key_results": [
            {
                "kr_id": "kr_1",
                "description": "Acquire 500 new users",
                "target": 500,
                "current": 325,
                "unit": "users",
                "progress": 65.0,
                "status": "on_track"
            },
            {
                "kr_id": "kr_2",
                "description": "Achieve 80% user retention",
                "target": 80,
                "current": 75,
                "unit": "percentage",
                "progress": 93.75,
                "status": "on_track"
            }
        ],
        "child_okrs": [],  # Cascaded OKRs
        "created_at": "2024-01-01T00:00:00",
        "last_updated": "2024-01-05T10:00:00"
    }

@router.put("/okrs/{okr_id}")
async def update_okr(okr_id: str, okr: OKR):
    """Update OKR"""
    
    # TODO: Update database
    # UPDATE okrs SET objective = %s, key_results = %s WHERE okr_id = %s
    
    return {
        "okr_id": okr_id,
        "updated_at": datetime.now().isoformat()
    }

@router.post("/okrs/{okr_id}/progress")
async def update_okr_progress(
    okr_id: str,
    key_result_updates: List[Dict[str, Any]]
):
    """Update progress on key results"""
    
    # key_result_updates: [{kr_id, current_value}]
    
    logger.info(f"Updating progress for OKR {okr_id}")
    
    # TODO:
    # 1. Update current values for each key result
    # 2. Recalculate overall progress
    # 3. Update status (on_track, at_risk, off_track)
    
    overall_progress = 65.0  # Calculated from all KRs
    
    return {
        "okr_id": okr_id,
        "overall_progress": overall_progress,
        "status": "on_track",
        "updated_at": datetime.now().isoformat()
    }

@router.get("/okrs/cascade")
async def get_cascading_okrs(parent_okr_id: Optional[str] = None):
    """View cascading OKRs hierarchy"""
    
    # TODO: Recursively get parent and child OKRs
    
    return {
        "company_okrs": [
            {
                "okr_id": "okr_company_1",
                "objective": "Become market leader in SaaS time tracking",
                "level": "company",
                "team_okrs": [
                    {
                        "okr_id": "okr_product_1",
                        "objective": "Increase product adoption by 50%",
                        "level": "team",
                        "individual_okrs": [
                            {
                                "okr_id": "okr_john_1",
                                "objective": "Launch 3 new product features",
                                "level": "individual"
                            }
                        ]
                    }
                ]
            }
        ]
    }

# ============================================================
# GOALS
# ============================================================

@router.post("/goals")
async def create_goal(goal: Goal):
    """Set an employee goal"""
    
    goal_id = f"goal_{hash(goal.employee_id + goal.description)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO goals (goal_id, employee_id, manager_id, goal_type, description, ...)
    
    return {
        "goal_id": goal_id,
        "employee_id": goal.employee_id,
        "description": goal.description,
        "target_date": goal.target_date.isoformat(),
        "created_at": datetime.now().isoformat()
    }

@router.get("/goals")
async def list_goals(
    employee_id: Optional[str] = None,
    status: Optional[str] = None
):
    """List employee goals"""
    
    return {
        "goals": [
            {
                "goal_id": "goal_1",
                "employee_id": "emp_1",
                "employee_name": "John Doe",
                "goal_type": "performance",
                "description": "Complete Python certification",
                "progress_percentage": 75.0,
                "target_date": "2024-06-30",
                "status": "active"
            }
        ],
        "total": 1
    }

@router.put("/goals/{goal_id}")
async def update_goal(goal_id: str, goal: Goal):
    """Update goal"""
    
    # TODO: Update database
    
    return {
        "goal_id": goal_id,
        "updated_at": datetime.now().isoformat()
    }

@router.put("/goals/{goal_id}/progress")
async def update_goal_progress(goal_id: str, progress_percentage: float):
    """Update goal progress"""
    
    if not (0 <= progress_percentage <= 100):
        raise HTTPException(status_code=400, detail="Progress must be between 0-100")
    
    # TODO: Update database
    # UPDATE goals SET progress_percentage = %s WHERE goal_id = %s
    
    # Mark as completed if 100%
    status = "completed" if progress_percentage >= 100 else "active"
    
    return {
        "goal_id": goal_id,
        "progress_percentage": progress_percentage,
        "status": status,
        "updated_at": datetime.now().isoformat()
    }

# ============================================================
# REVIEW CYCLES
# ============================================================

@router.post("/cycles")
async def create_review_cycle(cycle: ReviewCycle):
    """Create a performance review cycle"""
    
    cycle_id = f"cycle_{hash(cycle.name)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO review_cycles (cycle_id, name, cycle_type, start_date, end_date, status)
    
    return {
        "cycle_id": cycle_id,
        "name": cycle.name,
        "cycle_type": cycle.cycle_type,
        "start_date": cycle.start_date.isoformat(),
        "end_date": cycle.end_date.isoformat(),
        "created_at": datetime.now().isoformat()
    }

@router.get("/cycles")
async def list_review_cycles(status: Optional[str] = None):
    """List review cycles"""
    
    return {
        "cycles": [
            {
                "cycle_id": "cycle_1",
                "name": "Q4 2024 Performance Review",
                "cycle_type": "quarterly",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "status": "active",
                "reviews_count": 45,
                "reviews_completed": 30
            }
        ]
    }

# ============================================================
# PERFORMANCE REVIEWS
# ============================================================

@router.post("/reviews")
async def create_review(review: PerformanceReview):
    """Create a performance review"""
    
    review_id = f"review_{hash(review.employee_id + review.cycle_id)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO performance_reviews (review_id, cycle_id, employee_id, reviewer_id, ...)
    
    return {
        "review_id": review_id,
        "employee_id": review.employee_id,
        "reviewer_id": review.reviewer_id,
        "review_type": review.review_type,
        "status": "draft",
        "created_at": datetime.now().isoformat()
    }

@router.get("/reviews")
async def list_reviews(
    cycle_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    status: Optional[str] = None
):
    """List performance reviews"""
    
    return {
        "reviews": [
            {
                "review_id": "review_1",
                "cycle_name": "Q4 2024",
                "employee_id": "emp_1",
                "employee_name": "John Doe",
                "reviewer_id": "mgr_1",
                "reviewer_name": "Jane Manager",
                "review_type": "manager",
                "overall_rating": 4,
                "status": "completed",
                "review_date": "2024-01-15"
            }
        ],
        "total": 1
    }

@router.get("/reviews/{review_id}")
async def get_review(review_id: str):
    """Get detailed review"""
    
    return {
        "review_id": review_id,
        "cycle_id": "cycle_1",
        "cycle_name": "Q4 2024 Performance Review",
        "employee_id": "emp_1",
        "employee_name": "John Doe",
        "reviewer_id": "mgr_1",
        "reviewer_name": "Jane Manager",
        "review_type": "manager",
        "overall_rating": 4,
        "competency_ratings": {
            "technical_skills": 5,
            "communication": 4,
            "teamwork": 4,
            "problem_solving": 5,
            "leadership": 3
        },
        "strengths": "Excellent technical skills and problem-solving abilities...",
        "areas_for_improvement": "Could improve leadership and delegation skills...",
        "goals_for_next_period": "1. Complete leadership training\n2. Mentor 2 junior developers",
        "status": "completed",
        "review_date": "2024-01-15",
        "created_at": "2024-01-10T10:00:00"
    }

@router.put("/reviews/{review_id}")
async def update_review(review_id: str, review: PerformanceReview):
    """Update performance review"""
    
    # TODO: Update database
    
    return {
        "review_id": review_id,
        "updated_at": datetime.now().isoformat()
    }

@router.post("/reviews/{review_id}/complete")
async def complete_review(review_id: str):
    """Mark review as complete and submit"""
    
    logger.info(f"Completing review {review_id}")
    
    # TODO:
    # 1. Validate review is complete (all required fields filled)
    # 2. Update status to 'completed'
    # 3. Notify employee
    # 4. Lock review from further edits
    
    # UPDATE performance_reviews SET status = 'completed' WHERE review_id = %s
    
    return {
        "review_id": review_id,
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    }

# ============================================================
# 360 FEEDBACK
# ============================================================

@router.post("/reviews/{review_id}/feedback")
async def add_feedback(
    review_id: str,
    feedback_type: str,  # 'peer', 'direct_report', 'manager'
    reviewer_id: str,
    feedback_text: str,
    rating: Optional[int] = None,
    is_anonymous: bool = False
):
    """Add feedback to a review (360 feedback)"""
    
    feedback_id = f"fb_{hash(review_id + reviewer_id)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO review_feedback (feedback_id, review_id, feedback_type, reviewer_id, ...)
    
    return {
        "feedback_id": feedback_id,
        "review_id": review_id,
        "feedback_type": feedback_type,
        "is_anonymous": is_anonymous,
        "submitted_at": datetime.now().isoformat()
    }

@router.get("/reviews/{review_id}/feedback")
async def get_review_feedback(review_id: str):
    """Get all feedback for a review"""
    
    return {
        "review_id": review_id,
        "feedback": [
            {
                "feedback_id": "fb_1",
                "feedback_type": "peer",
                "reviewer_name": "Alice Smith" if not is_anonymous else "Anonymous",
                "feedback_text": "Great team player, always willing to help...",
                "rating": 5,
                "is_anonymous": False,
                "submitted_at": "2024-01-12T14:30:00"
            }
        ],
        "summary": {
            "total_feedback": 5,
            "peer_feedback": 3,
            "manager_feedback": 1,
            "direct_report_feedback": 1,
            "average_rating": 4.2
        }
    }

# ============================================================
# ANALYTICS
# ============================================================

@router.get("/analytics/ratings-distribution")
async def get_ratings_distribution(cycle_id: Optional[str] = None):
    """Get distribution of ratings"""
    
    return {
        "cycle_id": cycle_id,
        "distribution": {
            "5": 12,  # Exceptional
            "4": 28,  # Exceeds expectations
            "3": 45,  # Meets expectations
            "2": 10,  # Needs improvement
            "1": 5    # Unsatisfactory
        },
        "average_rating": 3.3,
        "calibration_needed": True  # If distribution is skewed
    }

@router.get("/analytics/goal-completion")
async def get_goal_completion_rates(
    start_date: date,
    end_date: date
):
    """Get goal completion statistics"""
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "total_goals": 250,
        "completed_goals": 185,
        "completion_rate": 74.0,
        "by_goal_type": {
            "performance": {"total": 100, "completed": 80, "rate": 80.0},
            "development": {"total": 100, "completed": 70, "rate": 70.0},
            "behavioral": {"total": 50, "completed": 35, "rate": 70.0}
        },
        "top_performers": [
            {"employee_name": "John Doe", "goals_completed": 8, "completion_rate": 100.0}
        ]
    }

logger.info("Performance Reviews routes loaded")
