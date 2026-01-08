"""
AI Router - REAL PREDICTIONS
Actual AI predictions using real employee data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.ai_engines.prediction_service import prediction_service

router = APIRouter()

class PredictionResponse(BaseModel):
    success: bool
    result: dict
    confidence: float
    warnings: list

@router.post("/predict/performance", response_model=PredictionResponse)
@require_permission(Permission.AI_VIEW_INSIGHTS)
async def predict_performance(
    employee_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict employee performance - REAL PREDICTION
    Uses actual historical time tracking data
    """
    tenant_id = current_user['tenant_id']
    
    try:
        result = prediction_service.predict_performance(db, employee_id, tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    log_audit_event(
        event_type='ai_predict_performance',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='ai',
        action='predict',
        details={'employee_id': employee_id, 'success': result['success']}
    )
    
    return result

@router.post("/predict/turnover", response_model=PredictionResponse)
@require_permission(Permission.AI_VIEW_INSIGHTS)
async def predict_turnover(
    employee_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict turnover risk - REAL PREDICTION
    Analyzes multiple risk factors from real data
    """
    tenant_id = current_user['tenant_id']
    
    try:
        result = prediction_service.predict_turnover(db, employee_id, tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    log_audit_event(
        event_type='ai_predict_turnover',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='ai',
        action='predict',
        details={'employee_id': employee_id, 'risk': result['result']['risk_category']}
    )
    
    return result

@router.get("/insights/team")
@require_permission(Permission.AI_VIEW_INSIGHTS)
async def get_team_insights(
    department: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get team-level AI insights - REAL AGGREGATION
    """
    tenant_id = current_user['tenant_id']
    
    result = prediction_service.get_team_insights(db, tenant_id, department)
    
    return result
