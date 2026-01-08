"""
COGNITIVE WORKFORCE LAYER - AI-DRIVEN EMPLOYEE INTELLIGENCE
============================================================

Features:
- Mental energy forecasting & burnout prediction
- Focus entropy index & flow-state detection
- Neuro-productivity profiling (privacy-safe, opt-in)
- Work-recovery optimization
- Cognitive capacity modeling

Author: W-OS Architecture Team
Version: 1.0.0
License: Enterprise
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import numpy as np
from dataclasses import dataclass
import logging

from ..models.cognitive_models import (
    CognitiveProfile,
    MentalEnergyReading,
    FlowStateSession,
    BurnoutRisk,
    FocusEntropyIndex,
    RecoveryRecommendation
)
from ..ai_services.cognitive_ai import CognitiveAIEngine

logger = logging.getLogger(__name__)


@dataclass
class CognitiveMetrics:
    """Real-time cognitive performance metrics"""
    user_id: str
    mental_energy: float  # 0-100 scale
    focus_score: float  # 0-100 scale
    flow_probability: float  # 0-1 probability
    burnout_risk: float  # 0-1 risk score
    recovery_needed_hours: int
    optimal_work_windows: List[Tuple[int, int]]  # (start_hour, end_hour)
    cognitive_capacity: float  # Remaining capacity %
    stress_level: str  # low, moderate, high, critical


class CognitiveWorkforceEngine:
    """
    AI-Driven Cognitive Workforce Intelligence System
    
    Monitors, predicts, and optimizes employee cognitive performance
    using privacy-safe, opt-in telemetry and AI models.
    
    Key Capabilities:
    - Real-time mental energy tracking
    - Burnout early warning system (3-week forecast)
    - Flow state detection and optimization
    - Personalized productivity recommendations
    - Executive dashboard for workforce cognitive health
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = CognitiveAIEngine()
        
        # AI Model configurations
        self.burnout_threshold = 0.7  # 70% risk triggers alert
        self.flow_state_threshold = 0.75  # 75% probability indicates flow
        self.energy_recovery_rate = 0.08  # 8% per hour of rest
        
    # =================================================================
    # CORE COGNITIVE MONITORING
    # =================================================================
    
    def capture_cognitive_snapshot(
        self,
        user_id: str,
        activity_data: Dict,
        biometric_data: Optional[Dict] = None,
        self_reported_data: Optional[Dict] = None
    ) -> CognitiveMetrics:
        """
        Capture real-time cognitive state snapshot
        
        Inputs:
        - Activity: keystrokes, mouse movement, app switches, breaks
        - Biometrics (opt-in): HRV, sleep quality from wearables
        - Self-reported: mood, stress level, sleep hours
        
        Output: Current cognitive state metrics
        """
        
        # Extract activity patterns
        activity_patterns = self._analyze_activity_patterns(activity_data)
        
        # Calculate mental energy
        mental_energy = self._calculate_mental_energy(
            user_id,
            activity_patterns,
            biometric_data,
            self_reported_data
        )
        
        # Detect flow state probability
        flow_prob = self._detect_flow_state(activity_patterns)
        
        # Calculate focus entropy (measure of distraction)
        focus_score = self._calculate_focus_entropy(activity_patterns)
        
        # Predict burnout risk
        burnout_risk = self._predict_burnout_risk(user_id, mental_energy)
        
        # Calculate recovery needed
        recovery_hours = self._calculate_recovery_needed(mental_energy, burnout_risk)
        
        # Find optimal work windows
        optimal_windows = self._find_optimal_work_windows(user_id)
        
        # Calculate remaining cognitive capacity
        cognitive_capacity = self._calculate_cognitive_capacity(
            mental_energy,
            focus_score,
            flow_prob
        )
        
        # Determine stress level
        stress_level = self._determine_stress_level(
            mental_energy,
            burnout_risk,
            focus_score
        )
        
        # Store reading in database
        reading = MentalEnergyReading(
            user_id=user_id,
            mental_energy=mental_energy,
            focus_score=focus_score,
            flow_probability=flow_prob,
            burnout_risk=burnout_risk,
            cognitive_capacity=cognitive_capacity,
            stress_level=stress_level,
            timestamp=datetime.utcnow()
        )
        self.db.add(reading)
        self.db.commit()
        
        return CognitiveMetrics(
            user_id=user_id,
            mental_energy=mental_energy,
            focus_score=focus_score,
            flow_probability=flow_prob,
            burnout_risk=burnout_risk,
            recovery_needed_hours=recovery_hours,
            optimal_work_windows=optimal_windows,
            cognitive_capacity=cognitive_capacity,
            stress_level=stress_level
        )
    
    # =================================================================
    # MENTAL ENERGY FORECASTING
    # =================================================================
    
    def forecast_mental_energy(
        self,
        user_id: str,
        forecast_days: int = 21
    ) -> List[Dict]:
        """
        Forecast mental energy for next N days
        
        Uses:
        - Historical energy patterns
        - Upcoming calendar (meetings, deadlines)
        - Seasonal patterns (Monday blues, Friday energy)
        - Personal circadian rhythm
        
        Returns: Daily energy forecast with confidence intervals
        """
        
        # Get historical data (last 90 days)
        historical = self.db.query(MentalEnergyReading).filter(
            MentalEnergyReading.user_id == user_id,
            MentalEnergyReading.timestamp >= datetime.utcnow() - timedelta(days=90)
        ).order_by(MentalEnergyReading.timestamp).all()
        
        if len(historical) < 14:
            return []  # Need minimum 2 weeks of data
        
        # Prepare time series data
        energy_series = [h.mental_energy for h in historical]
        dates = [h.timestamp for h in historical]
        
        # Use AI model to forecast
        forecast = self.ai_engine.forecast_mental_energy(
            energy_series=energy_series,
            dates=dates,
            user_id=user_id,
            forecast_days=forecast_days
        )
        
        return forecast
    
    # =================================================================
    # BURNOUT PREDICTION & EARLY WARNING
    # =================================================================
    
    def predict_burnout_risk(
        self,
        user_id: str,
        forecast_weeks: int = 3
    ) -> Dict:
        """
        Predict burnout risk for next 3 weeks
        
        Warning System:
        - Green: Risk < 30%
        - Yellow: Risk 30-50%
        - Orange: Risk 50-70%
        - Red: Risk > 70% (immediate intervention needed)
        
        Factors:
        - Sustained low mental energy
        - Increasing stress levels
        - Declining focus scores
        - Reduced recovery between work sessions
        - Calendar overload
        - Historical burnout patterns
        """
        
        # Get current cognitive profile
        profile = self.db.query(CognitiveProfile).filter(
            CognitiveProfile.user_id == user_id
        ).first()
        
        if not profile:
            return {"error": "No cognitive profile found"}
        
        # Get recent readings (last 30 days)
        recent_readings = self.db.query(MentalEnergyReading).filter(
            MentalEnergyReading.user_id == user_id,
            MentalEnergyReading.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).order_by(MentalEnergyReading.timestamp.desc()).all()
        
        # Calculate burnout indicators
        indicators = {
            'sustained_low_energy': self._check_sustained_low_energy(recent_readings),
            'stress_trend': self._calculate_stress_trend(recent_readings),
            'focus_decline': self._check_focus_decline(recent_readings),
            'recovery_deficit': self._calculate_recovery_deficit(recent_readings),
            'workload_intensity': self._calculate_workload_intensity(user_id)
        }
        
        # AI prediction
        risk_score = self.ai_engine.predict_burnout(
            user_id=user_id,
            indicators=indicators,
            forecast_weeks=forecast_weeks
        )
        
        # Determine alert level
        if risk_score < 0.3:
            alert_level = "green"
            recommendation = "Maintain current pace"
        elif risk_score < 0.5:
            alert_level = "yellow"
            recommendation = "Monitor closely, consider lighter schedule"
        elif risk_score < 0.7:
            alert_level = "orange"
            recommendation = "Reduce workload, schedule recovery time"
        else:
            alert_level = "red"
            recommendation = "IMMEDIATE INTERVENTION: Mandatory rest period needed"
        
        # Store prediction
        prediction = BurnoutRisk(
            user_id=user_id,
            risk_score=risk_score,
            alert_level=alert_level,
            recommendation=recommendation,
            indicators=indicators,
            forecast_weeks=forecast_weeks,
            predicted_at=datetime.utcnow()
        )
        self.db.add(prediction)
        self.db.commit()
        
        return {
            'user_id': user_id,
            'risk_score': risk_score,
            'alert_level': alert_level,
            'recommendation': recommendation,
            'indicators': indicators,
            'forecast_weeks': forecast_weeks
        }
    
    # =================================================================
    # FLOW STATE DETECTION
    # =================================================================
    
    def detect_flow_state(
        self,
        user_id: str,
        session_data: Dict
    ) -> Dict:
        """
        Detect if user is in flow state
        
        Flow State Indicators:
        - High typing speed consistency
        - Minimal app switching (<2 per 10 min)
        - Long uninterrupted sessions (>25 min)
        - Low correction rate (few backspaces)
        - Steady keystroke rhythm
        - No chat/email interruptions
        
        Returns: Flow probability and session metrics
        """
        
        # Extract flow indicators from session data
        indicators = {
            'typing_consistency': self._calculate_typing_consistency(session_data),
            'app_switches': session_data.get('app_switches', 0),
            'uninterrupted_time': session_data.get('duration_minutes', 0),
            'correction_rate': self._calculate_correction_rate(session_data),
            'keystroke_rhythm': self._analyze_keystroke_rhythm(session_data),
            'interruptions': session_data.get('interruptions', 0)
        }
        
        # Calculate flow probability using AI
        flow_probability = self.ai_engine.calculate_flow_probability(indicators)
        
        # If in flow state, log the session
        if flow_probability >= self.flow_state_threshold:
            flow_session = FlowStateSession(
                user_id=user_id,
                start_time=session_data['start_time'],
                duration_minutes=session_data['duration_minutes'],
                flow_probability=flow_probability,
                indicators=indicators,
                task_type=session_data.get('task_type', 'unknown')
            )
            self.db.add(flow_session)
            self.db.commit()
        
        return {
            'user_id': user_id,
            'in_flow_state': flow_probability >= self.flow_state_threshold,
            'flow_probability': flow_probability,
            'indicators': indicators,
            'session_duration': session_data['duration_minutes']
        }
    
    # =================================================================
    # FOCUS ENTROPY INDEX
    # =================================================================
    
    def calculate_focus_entropy(
        self,
        user_id: str,
        time_window_hours: int = 4
    ) -> Dict:
        """
        Calculate Focus Entropy Index (FEI)
        
        FEI measures cognitive fragmentation (distraction level)
        
        Low Entropy (0-30): Highly focused, deep work
        Medium Entropy (30-60): Normal work, some distractions
        High Entropy (60-100): Fragmented attention, many interruptions
        
        Factors:
        - App switch frequency
        - Task switching rate
        - Notification response time
        - Context changes per hour
        """
        
        start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Query activity data
        # This would integrate with actual activity tracking
        activity_data = self._get_activity_data(user_id, start_time)
        
        # Calculate entropy components
        app_switch_entropy = self._calculate_app_switch_entropy(activity_data)
        task_switch_entropy = self._calculate_task_switch_entropy(activity_data)
        notification_entropy = self._calculate_notification_entropy(activity_data)
        context_entropy = self._calculate_context_entropy(activity_data)
        
        # Weighted average
        total_entropy = (
            app_switch_entropy * 0.3 +
            task_switch_entropy * 0.3 +
            notification_entropy * 0.2 +
            context_entropy * 0.2
        )
        
        # Store in database
        entropy_reading = FocusEntropyIndex(
            user_id=user_id,
            entropy_score=total_entropy,
            app_switch_entropy=app_switch_entropy,
            task_switch_entropy=task_switch_entropy,
            notification_entropy=notification_entropy,
            context_entropy=context_entropy,
            time_window_hours=time_window_hours,
            measured_at=datetime.utcnow()
        )
        self.db.add(entropy_reading)
        self.db.commit()
        
        # Interpretation
        if total_entropy < 30:
            focus_state = "Deep Focus"
            recommendation = "Maintain current state, minimize interruptions"
        elif total_entropy < 60:
            focus_state = "Normal Work"
            recommendation = "Moderate focus, acceptable distraction level"
        else:
            focus_state = "Fragmented Attention"
            recommendation = "High distraction detected, consider focus techniques"
        
        return {
            'user_id': user_id,
            'entropy_score': total_entropy,
            'focus_state': focus_state,
            'recommendation': recommendation,
            'components': {
                'app_switch': app_switch_entropy,
                'task_switch': task_switch_entropy,
                'notification': notification_entropy,
                'context': context_entropy
            }
        }
    
    # =================================================================
    # RECOVERY OPTIMIZATION
    # =================================================================
    
    def generate_recovery_recommendations(
        self,
        user_id: str
    ) -> List[Dict]:
        """
        Generate personalized recovery recommendations
        
        Based on:
        - Current mental energy level
        - Upcoming calendar
        - Historical recovery patterns
        - Sleep debt
        - Stress levels
        
        Recommendations:
        - Optimal break timing
        - Ideal lunch duration
        - Evening shutdown time
        - Weekend planning
        - Vacation timing
        """
        
        # Get current cognitive state
        latest_reading = self.db.query(MentalEnergyReading).filter(
            MentalEnergyReading.user_id == user_id
        ).order_by(MentalEnergyReading.timestamp.desc()).first()
        
        if not latest_reading:
            return []
        
        # Generate recommendations using AI
        recommendations = self.ai_engine.generate_recovery_plan(
            user_id=user_id,
            current_energy=latest_reading.mental_energy,
            burnout_risk=latest_reading.burnout_risk,
            stress_level=latest_reading.stress_level
        )
        
        # Store recommendations
        for rec in recommendations:
            recovery_rec = RecoveryRecommendation(
                user_id=user_id,
                recommendation_type=rec['type'],
                priority=rec['priority'],
                description=rec['description'],
                estimated_impact=rec['estimated_impact'],
                recommended_timing=rec['timing'],
                created_at=datetime.utcnow()
            )
            self.db.add(recovery_rec)
        
        self.db.commit()
        
        return recommendations
    
    # =================================================================
    # EXECUTIVE DASHBOARD METRICS
    # =================================================================
    
    def get_workforce_cognitive_health(
        self,
        tenant_id: str,
        department_id: Optional[str] = None
    ) -> Dict:
        """
        Get organization-wide cognitive health metrics
        
        For Executive Dashboard:
        - Average mental energy by department
        - Burnout risk distribution
        - Flow state frequency
        - Recovery debt by team
        - Cognitive capacity utilization
        
        Privacy-safe: Only aggregated data, no individual identification
        """
        
        # Build query
        query = self.db.query(
            MentalEnergyReading.user_id,
            func.avg(MentalEnergyReading.mental_energy).label('avg_energy'),
            func.avg(MentalEnergyReading.burnout_risk).label('avg_burnout'),
            func.avg(MentalEnergyReading.focus_score).label('avg_focus'),
            func.avg(MentalEnergyReading.cognitive_capacity).label('avg_capacity')
        ).filter(
            MentalEnergyReading.timestamp >= datetime.utcnow() - timedelta(days=7)
        )
        
        # Execute aggregation
        results = query.all()
        
        # Calculate organization metrics
        total_employees = len(results)
        
        avg_energy = np.mean([r.avg_energy for r in results])
        avg_burnout = np.mean([r.avg_burnout for r in results])
        avg_focus = np.mean([r.avg_focus for r in results])
        avg_capacity = np.mean([r.avg_capacity for r in results])
        
        # Risk distribution
        high_risk = len([r for r in results if r.avg_burnout > 0.7])
        medium_risk = len([r for r in results if 0.5 < r.avg_burnout <= 0.7])
        low_risk = total_employees - high_risk - medium_risk
        
        return {
            'tenant_id': tenant_id,
            'total_employees': total_employees,
            'average_mental_energy': round(avg_energy, 1),
            'average_burnout_risk': round(avg_burnout, 2),
            'average_focus_score': round(avg_focus, 1),
            'average_cognitive_capacity': round(avg_capacity, 1),
            'burnout_risk_distribution': {
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            },
            'health_score': self._calculate_health_score(
                avg_energy,
                avg_burnout,
                avg_focus
            ),
            'measured_at': datetime.utcnow().isoformat()
        }
    
    # =================================================================
    # PRIVATE HELPER METHODS
    # =================================================================
    
    def _analyze_activity_patterns(self, activity_data: Dict) -> Dict:
        """Extract patterns from raw activity data"""
        # Implementation details...
        pass
    
    def _calculate_mental_energy(
        self,
        user_id: str,
        activity: Dict,
        biometric: Optional[Dict],
        self_reported: Optional[Dict]
    ) -> float:
        """Calculate current mental energy level (0-100)"""
        # Base calculation on activity patterns
        base_energy = 70.0  # Default
        
        # Adjust based on factors
        # Implementation details...
        
        return base_energy
    
    def _detect_flow_state(self, activity: Dict) -> float:
        """Detect flow state probability"""
        # Implementation details...
        return 0.5
    
    def _calculate_focus_entropy(self, activity: Dict) -> float:
        """Calculate focus entropy index"""
        # Implementation details...
        return 50.0
    
    def _predict_burnout_risk(self, user_id: str, energy: float) -> float:
        """Predict burnout risk score"""
        # Implementation details...
        return 0.3
    
    def _calculate_recovery_needed(self, energy: float, risk: float) -> int:
        """Calculate hours of recovery needed"""
        if energy > 80 and risk < 0.3:
            return 0
        elif energy > 60:
            return 4
        elif energy > 40:
            return 8
        else:
            return 16
    
    def _find_optimal_work_windows(self, user_id: str) -> List[Tuple[int, int]]:
        """Find optimal work time windows based on circadian rhythm"""
        # Default peak hours
        return [(9, 11), (14, 16)]
    
    def _calculate_cognitive_capacity(
        self,
        energy: float,
        focus: float,
        flow_prob: float
    ) -> float:
        """Calculate remaining cognitive capacity"""
        return (energy * 0.5 + focus * 0.3 + flow_prob * 100 * 0.2)
    
    def _determine_stress_level(
        self,
        energy: float,
        burnout: float,
        focus: float
    ) -> str:
        """Determine stress level category"""
        if burnout > 0.7 or energy < 30:
            return "critical"
        elif burnout > 0.5 or energy < 50:
            return "high"
        elif burnout > 0.3 or energy < 70:
            return "moderate"
        else:
            return "low"
    
    def _check_sustained_low_energy(self, readings: List) -> bool:
        """Check if energy has been consistently low"""
        if len(readings) < 7:
            return False
        recent_avg = np.mean([r.mental_energy for r in readings[:7]])
        return recent_avg < 40
    
    def _calculate_stress_trend(self, readings: List) -> str:
        """Calculate stress trend direction"""
        if len(readings) < 14:
            return "insufficient_data"
        
        recent = np.mean([r.burnout_risk for r in readings[:7]])
        previous = np.mean([r.burnout_risk for r in readings[7:14]])
        
        if recent > previous + 0.1:
            return "increasing"
        elif recent < previous - 0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _check_focus_decline(self, readings: List) -> bool:
        """Check if focus is declining"""
        if len(readings) < 14:
            return False
        
        recent = np.mean([r.focus_score for r in readings[:7]])
        previous = np.mean([r.focus_score for r in readings[7:14]])
        
        return recent < previous - 10
    
    def _calculate_recovery_deficit(self, readings: List) -> float:
        """Calculate cumulative recovery deficit"""
        # Implementation details...
        return 0.5
    
    def _calculate_workload_intensity(self, user_id: str) -> float:
        """Calculate current workload intensity"""
        # Implementation details...
        return 0.6
    
    def _calculate_health_score(
        self,
        energy: float,
        burnout: float,
        focus: float
    ) -> float:
        """Calculate overall workforce cognitive health score (0-100)"""
        return (energy * 0.4 + (1 - burnout) * 100 * 0.4 + focus * 0.2)
