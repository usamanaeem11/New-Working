"""
Business Intelligence & Predictive Analytics
KPI tracking, ROI calculations, profitability analysis, and trend forecasting
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from pydantic import BaseModel
import logging
import statistics

router = APIRouter(prefix="/api/bi", tags=["Business Intelligence"])
logger = logging.getLogger(__name__)

# ============================================================
# MODELS
# ============================================================

class KPIDefinition(BaseModel):
    kpi_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    formula: str  # SQL query or calculation formula
    unit: str  # 'percentage', 'currency', 'number', 'hours'
    target_value: float
    warning_threshold: float
    critical_threshold: float
    calculation_frequency: str = "daily"  # daily, weekly, monthly

class Dashboard(BaseModel):
    dashboard_id: Optional[str] = None
    name: str
    user_id: str
    layout: Dict[str, Any]  # Grid layout configuration
    widgets: List[Dict[str, Any]]  # Widget definitions
    is_shared: bool = False

# ============================================================
# KPI MANAGEMENT
# ============================================================

@router.post("/kpis")
async def create_kpi(kpi: KPIDefinition):
    """Define a new KPI"""
    logger.info(f"Creating KPI: {kpi.name}")
    
    kpi_id = f"kpi_{hash(kpi.name)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO kpi_definitions (kpi_id, name, formula, unit, target_value, ...)
    
    return {
        "kpi_id": kpi_id,
        "name": kpi.name,
        "created_at": datetime.now().isoformat()
    }

@router.get("/kpis")
async def list_kpis():
    """List all KPI definitions"""
    
    return {
        "kpis": [
            {
                "kpi_id": "kpi_1",
                "name": "Employee Utilization Rate",
                "unit": "percentage",
                "target_value": 80.0,
                "current_value": 75.3,
                "status": "warning"
            },
            {
                "kpi_id": "kpi_2",
                "name": "Project Profitability",
                "unit": "percentage",
                "target_value": 25.0,
                "current_value": 28.5,
                "status": "good"
            },
            {
                "kpi_id": "kpi_3",
                "name": "Invoice Collection Time",
                "unit": "days",
                "target_value": 30.0,
                "current_value": 42.0,
                "status": "critical"
            }
        ]
    }

@router.get("/kpis/{kpi_id}/calculate")
async def calculate_kpi(
    kpi_id: str,
    start_date: date,
    end_date: date
):
    """Calculate KPI value for a period"""
    
    # TODO: 
    # 1. Get KPI definition from database
    # 2. Execute formula/query
    # 3. Compare against thresholds
    # 4. Store in kpi_values table
    
    calculated_value = 75.3  # Result from formula execution
    target_value = 80.0
    
    # Determine status
    status = "good"
    if calculated_value < 70.0:  # critical_threshold
        status = "critical"
    elif calculated_value < 75.0:  # warning_threshold
        status = "warning"
    
    return {
        "kpi_id": kpi_id,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "calculated_value": calculated_value,
        "target_value": target_value,
        "variance": calculated_value - target_value,
        "variance_percentage": ((calculated_value - target_value) / target_value) * 100,
        "status": status,
        "calculated_at": datetime.now().isoformat()
    }

@router.put("/kpis/{kpi_id}")
async def update_kpi(kpi_id: str, kpi: KPIDefinition):
    """Update KPI definition"""
    
    return {
        "kpi_id": kpi_id,
        "updated_at": datetime.now().isoformat()
    }

# ============================================================
# PREDICTIVE ANALYTICS
# ============================================================

@router.post("/predictions/project-delay")
async def predict_project_delay(project_id: str):
    """Predict probability of project delay"""
    
    # TODO: ML model or statistical analysis
    # Factors:
    # - Current progress vs timeline
    # - Resource allocation
    # - Historical team performance
    # - Task complexity
    # - Dependencies
    
    # Simplified calculation for demo
    delay_probability = 35.5  # 35.5% chance of delay
    expected_delay_days = 5
    
    factors = [
        {"factor": "Progress behind schedule", "impact": "high", "contribution": 15.0},
        {"factor": "Resource utilization low", "impact": "medium", "contribution": 10.5},
        {"factor": "Complex dependencies", "impact": "medium", "contribution": 10.0}
    ]
    
    return {
        "project_id": project_id,
        "delay_probability": delay_probability,
        "risk_level": "medium",  # low, medium, high
        "expected_delay_days": expected_delay_days if delay_probability > 50 else 0,
        "confidence_level": 78.5,
        "contributing_factors": factors,
        "recommendations": [
            "Allocate additional resources to critical path tasks",
            "Review and optimize task dependencies",
            "Increase team utilization rate"
        ],
        "predicted_at": datetime.now().isoformat()
    }

@router.post("/predictions/budget-overrun")
async def predict_budget_overrun(project_id: str):
    """Predict probability of budget overrun"""
    
    # TODO: Calculate based on:
    # - Current spend rate
    # - Remaining budget
    # - Remaining timeline
    # - Historical burn rate
    
    budget_total = 100000
    budget_spent = 65000
    budget_remaining = 35000
    progress_percentage = 55.0
    
    # If 65% spent but only 55% complete -> overrun likely
    spend_rate = (budget_spent / budget_total) * 100
    overrun_probability = max(0, spend_rate - progress_percentage) * 2
    
    expected_final_cost = (budget_spent / progress_percentage) * 100 if progress_percentage > 0 else budget_total
    expected_overrun = expected_final_cost - budget_total
    
    return {
        "project_id": project_id,
        "budget_total": budget_total,
        "budget_spent": budget_spent,
        "budget_remaining": budget_remaining,
        "progress_percentage": progress_percentage,
        "overrun_probability": min(100, overrun_probability),
        "risk_level": "high" if overrun_probability > 70 else "medium" if overrun_probability > 40 else "low",
        "expected_final_cost": expected_final_cost,
        "expected_overrun": max(0, expected_overrun),
        "recommendations": [
            "Review and reduce scope",
            "Optimize resource allocation",
            "Renegotiate timeline or budget with client"
        ],
        "predicted_at": datetime.now().isoformat()
    }

@router.get("/predictions/trends")
async def analyze_trends(
    metric: str,
    start_date: date,
    end_date: date
):
    """Analyze trends and forecast future values"""
    
    # TODO: Time series analysis
    # Get historical data, fit trend line, forecast future
    
    historical_values = [
        {"period": "2024-W1", "value": 75.5},
        {"period": "2024-W2", "value": 78.2},
        {"period": "2024-W3", "value": 76.8},
        {"period": "2024-W4", "value": 80.1}
    ]
    
    # Simple linear regression for demo
    values = [d["value"] for d in historical_values]
    avg_value = statistics.mean(values)
    trend_direction = "up" if values[-1] > values[0] else "down"
    
    # Forecast next 4 weeks
    growth_rate = (values[-1] - values[0]) / len(values)
    forecast = [
        {"period": "2024-W5", "predicted_value": values[-1] + growth_rate * 1, "confidence": 85.0},
        {"period": "2024-W6", "predicted_value": values[-1] + growth_rate * 2, "confidence": 78.0},
        {"period": "2024-W7", "predicted_value": values[-1] + growth_rate * 3, "confidence": 70.0},
        {"period": "2024-W8", "predicted_value": values[-1] + growth_rate * 4, "confidence": 62.0}
    ]
    
    return {
        "metric": metric,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "historical_data": historical_values,
        "trend_direction": trend_direction,
        "average_value": avg_value,
        "growth_rate": growth_rate,
        "forecast": forecast,
        "analysis_date": datetime.now().isoformat()
    }

# ============================================================
# ROI CALCULATIONS
# ============================================================

@router.post("/roi/project/{project_id}")
async def calculate_project_roi(project_id: str):
    """Calculate comprehensive ROI for a project"""
    
    # TODO: Get project financials from database
    # - Total revenue (actual + projected)
    # - Total costs (labor + expenses)
    # - Timeline
    
    total_revenue = 150000
    total_cost = 98000
    profit = total_revenue - total_cost
    roi_percentage = (profit / total_cost) * 100
    
    # Calculate NPV (simplified)
    discount_rate = 0.10  # 10% annual discount rate
    project_months = 6
    npv = profit / ((1 + discount_rate) ** (project_months / 12))
    
    # Calculate IRR (simplified)
    irr = (profit / total_cost) * (12 / project_months) * 100
    
    # Payback period
    monthly_profit = profit / project_months
    payback_months = total_cost / monthly_profit if monthly_profit > 0 else 0
    
    return {
        "project_id": project_id,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "gross_profit": profit,
        "profit_margin": (profit / total_revenue) * 100,
        "roi_percentage": roi_percentage,
        "npv": npv,
        "irr": irr,
        "payback_period_months": payback_months,
        "cost_breakdown": {
            "labor": 85000,
            "expenses": 13000
        },
        "revenue_breakdown": {
            "fixed_fee": 100000,
            "hourly_billing": 50000
        },
        "calculated_at": datetime.now().isoformat()
    }

@router.get("/roi/summary")
async def get_roi_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get ROI summary across all projects"""
    
    return {
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "total_projects": 25,
        "total_revenue": 3750000,
        "total_cost": 2450000,
        "total_profit": 1300000,
        "average_roi": 53.06,
        "best_performing_project": {
            "project_id": "proj_123",
            "name": "Enterprise CRM Implementation",
            "roi": 125.5
        },
        "worst_performing_project": {
            "project_id": "proj_456",
            "name": "Mobile App Development",
            "roi": 12.3
        },
        "roi_distribution": {
            "excellent": 8,  # >70% ROI
            "good": 12,  # 40-70% ROI
            "fair": 4,  # 20-40% ROI
            "poor": 1  # <20% ROI
        }
    }

# ============================================================
# PROFITABILITY ANALYSIS
# ============================================================

@router.get("/profitability/projects")
async def analyze_project_profitability(
    status: Optional[str] = None,
    client_id: Optional[str] = None
):
    """Analyze profitability by project"""
    
    return {
        "projects": [
            {
                "project_id": "proj_1",
                "project_name": "Website Redesign",
                "client": "Acme Corp",
                "revenue": 50000,
                "cost": 32000,
                "profit": 18000,
                "profit_margin": 36.0,
                "status": "excellent"
            },
            {
                "project_id": "proj_2",
                "project_name": "Mobile App",
                "client": "Tech Startup",
                "revenue": 80000,
                "cost": 75000,
                "profit": 5000,
                "profit_margin": 6.25,
                "status": "poor"
            }
        ],
        "summary": {
            "total_revenue": 130000,
            "total_cost": 107000,
            "total_profit": 23000,
            "average_margin": 21.1
        }
    }

@router.get("/profitability/clients")
async def analyze_client_profitability():
    """Analyze profitability by client"""
    
    return {
        "clients": [
            {
                "client_id": "client_1",
                "client_name": "Acme Corp",
                "total_projects": 5,
                "total_revenue": 250000,
                "total_cost": 175000,
                "total_profit": 75000,
                "profit_margin": 30.0,
                "lifetime_value": 250000,
                "acquisition_cost": 5000,
                "ltv_cac_ratio": 50.0
            }
        ]
    }

@router.get("/profitability/departments")
async def analyze_department_profitability():
    """Analyze profitability by department/team"""
    
    return {
        "departments": [
            {
                "department": "Engineering",
                "revenue_generated": 500000,
                "costs": 350000,
                "profit": 150000,
                "profit_margin": 30.0,
                "utilization_rate": 78.5
            },
            {
                "department": "Design",
                "revenue_generated": 200000,
                "costs": 150000,
                "profit": 50000,
                "profit_margin": 25.0,
                "utilization_rate": 82.0
            }
        ]
    }

# ============================================================
# CUSTOM DASHBOARDS
# ============================================================

@router.post("/dashboards")
async def create_dashboard(dashboard: Dashboard):
    """Create a custom dashboard"""
    
    dashboard_id = f"dash_{hash(dashboard.name + dashboard.user_id)}"[:16]
    
    # TODO: Insert into database
    # INSERT INTO custom_dashboards (dashboard_id, name, user_id, layout, widgets, is_shared)
    
    return {
        "dashboard_id": dashboard_id,
        "name": dashboard.name,
        "created_at": datetime.now().isoformat()
    }

@router.get("/dashboards")
async def list_dashboards(user_id: str, include_shared: bool = True):
    """List user's dashboards"""
    
    return {
        "dashboards": [
            {
                "dashboard_id": "dash_1",
                "name": "Executive Summary",
                "owner": user_id,
                "is_shared": False,
                "widget_count": 6
            },
            {
                "dashboard_id": "dash_2",
                "name": "Project Performance",
                "owner": user_id,
                "is_shared": True,
                "widget_count": 8
            }
        ]
    }

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard configuration and data"""
    
    return {
        "dashboard_id": dashboard_id,
        "name": "Executive Summary",
        "layout": {
            "cols": 12,
            "rows": 6
        },
        "widgets": [
            {
                "widget_id": "w1",
                "type": "kpi_card",
                "title": "Total Revenue",
                "data_source": "kpi_revenue",
                "position": {"x": 0, "y": 0, "w": 3, "h": 2},
                "config": {"format": "currency"}
            },
            {
                "widget_id": "w2",
                "type": "line_chart",
                "title": "Revenue Trend",
                "data_source": "revenue_by_month",
                "position": {"x": 3, "y": 0, "w": 6, "h": 4}
            }
        ]
    }

# ============================================================
# WHAT-IF SCENARIOS
# ============================================================

@router.post("/scenarios/analyze")
async def analyze_scenario(
    scenario_type: str,
    parameters: Dict[str, Any]
):
    """Run what-if scenario analysis"""
    
    # Example: "What if we increase prices by 10%?"
    # Example: "What if we reduce team size by 2 people?"
    
    if scenario_type == "price_change":
        price_increase_pct = parameters.get("price_increase_pct", 0)
        current_revenue = 100000
        current_customers = 100
        
        # Assume some customer churn based on price increase
        churn_rate = min(price_increase_pct / 2, 20)  # Max 20% churn
        new_customers = current_customers * (1 - churn_rate / 100)
        new_price = current_revenue / current_customers * (1 + price_increase_pct / 100)
        new_revenue = new_customers * new_price
        
        return {
            "scenario": "price_change",
            "parameters": parameters,
            "current_state": {
                "revenue": current_revenue,
                "customers": current_customers,
                "avg_price": current_revenue / current_customers
            },
            "projected_state": {
                "revenue": new_revenue,
                "customers": new_customers,
                "avg_price": new_price
            },
            "impact": {
                "revenue_change": new_revenue - current_revenue,
                "revenue_change_pct": ((new_revenue - current_revenue) / current_revenue) * 100,
                "customer_churn": current_customers - new_customers
            }
        }
    
    return {"scenario": scenario_type, "message": "Scenario analysis not implemented for this type"}

logger.info("Business Intelligence routes loaded")
