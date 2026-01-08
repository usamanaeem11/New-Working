"""
AI-Powered Rewards Engine
Detects opportunities, suggests rewards, validates auto-awards
"""

from typing import List, Dict
import numpy as np
from datetime import datetime, timedelta

class AIRewardsEngine:
    """AI engine for intelligent reward suggestions"""
    
    def __init__(self, ml_models):
        self.models = ml_models
        
    def analyze_reward_opportunities(
        self,
        employee: Dict,
        metrics: Dict,
        history: List[Dict]
    ) -> List[Dict]:
        """
        Analyze employee data and find reward opportunities
        
        Returns list of opportunities with:
        - reward_type: badge/points/bonus
        - reasoning: Why this reward
        - confidence: 0-1 score
        - value: Points/$ amount
        - auto_award_eligible: Can auto-award?
        """
        opportunities = []
        
        # Check attendance patterns
        if self._check_perfect_attendance(metrics):
            opportunities.append({
                'reward_type': 'badge',
                'badge_id': 'perfect_attendance_month',
                'reasoning': 'Perfect attendance for 30 consecutive days',
                'confidence': 0.95,
                'value': 200,
                'auto_award_eligible': True
            })
        
        # Check productivity
        if self._check_top_performer(employee, metrics):
            opportunities.append({
                'reward_type': 'bonus',
                'reasoning': 'Top 5% productivity this month',
                'confidence': 0.88,
                'value': 500.0,  # $500 bonus
                'auto_award_eligible': False  # Needs manager approval
            })
        
        # Check cognitive health
        if self._check_burnout_avoidance(metrics):
            opportunities.append({
                'reward_type': 'badge',
                'badge_id': 'burnout_avoider',
                'reasoning': 'Maintained low burnout risk for 30 days',
                'confidence': 0.92,
                'value': 200,
                'auto_award_eligible': True
            })
        
        # Check flow state achievement
        if self._check_flow_state_mastery(metrics):
            opportunities.append({
                'reward_type': 'badge',
                'badge_id': 'flow_state_expert',
                'reasoning': 'Achieved flow state 20+ times this month',
                'confidence': 0.90,
                'value': 300,
                'auto_award_eligible': True
            })
        
        # Check team collaboration
        if self._check_team_collaboration(metrics):
            opportunities.append({
                'reward_type': 'badge',
                'badge_id': 'team_player',
                'reasoning': 'Helped 10+ team members this month',
                'confidence': 0.85,
                'value': 150,
                'auto_award_eligible': False
            })
        
        # Check for exceptional improvement
        if self._check_exceptional_improvement(metrics, history):
            opportunities.append({
                'reward_type': 'bonus',
                'reasoning': 'Productivity improved 50% over last quarter',
                'confidence': 0.82,
                'value': 1000.0,
                'auto_award_eligible': False
            })
        
        return opportunities
    
    def validate_auto_award(self, employee_id: str, trigger: str) -> Dict:
        """
        Validate if auto-award should be given
        
        Returns:
        - approved: bool
        - reward_type: badge/points
        - value: amount
        - reasoning: why
        """
        validation_rules = {
            'perfect_attendance_7_days': {
                'approved': True,
                'reward_type': 'badge',
                'badge_id': 'perfect_attendance_week',
                'value': 50,
                'reasoning': '7 consecutive days without absence'
            },
            'task_completed_100': {
                'approved': True,
                'reward_type': 'badge',
                'badge_id': 'task_master',
                'value': 300,
                'reasoning': 'Completed 100 tasks milestone'
            },
            'early_arrival_20': {
                'approved': True,
                'reward_type': 'badge',
                'badge_id': 'early_bird',
                'value': 100,
                'reasoning': 'Arrived early 20 times'
            }
        }
        
        return validation_rules.get(trigger, {'approved': False})
    
    def learn_from_rejection(self, reward: Dict, reason: str):
        """
        Learn from manager rejections to improve AI
        
        Updates ML models based on rejection feedback
        """
        # Log rejection for training data
        self._log_rejection(reward, reason)
        
        # Update confidence thresholds
        if 'overvalued' in reason.lower():
            self._adjust_value_model(reward, direction='down')
        elif 'undervalued' in reason.lower():
            self._adjust_value_model(reward, direction='up')
        
        # Retrain models periodically
        self._schedule_model_retrain()
    
    # Helper methods
    def _check_perfect_attendance(self, metrics: Dict) -> bool:
        attendance = metrics.get('attendance', {})
        return attendance.get('consecutive_days_present', 0) >= 30
    
    def _check_top_performer(self, employee: Dict, metrics: Dict) -> bool:
        # Check if in top 5% of department
        percentile = metrics.get('productivity_percentile', 0)
        return percentile >= 95
    
    def _check_burnout_avoidance(self, metrics: Dict) -> bool:
        burnout_history = metrics.get('burnout_risk_history', [])
        if len(burnout_history) < 30:
            return False
        recent = burnout_history[-30:]
        return all(risk < 30 for risk in recent)  # All below 30% risk
    
    def _check_flow_state_mastery(self, metrics: Dict) -> bool:
        flow_count = metrics.get('flow_state_count_month', 0)
        return flow_count >= 20
    
    def _check_team_collaboration(self, metrics: Dict) -> bool:
        help_count = metrics.get('team_members_helped', 0)
        return help_count >= 10
    
    def _check_exceptional_improvement(
        self,
        metrics: Dict,
        history: List[Dict]
    ) -> bool:
        current_productivity = metrics.get('productivity_score', 0)
        
        # Get productivity 90 days ago
        if not history:
            return False
        
        past_productivity = history[0].get('productivity_score', 0)
        
        if past_productivity == 0:
            return False
        
        improvement = (current_productivity - past_productivity) / past_productivity
        return improvement >= 0.50  # 50% improvement
    
    def _log_rejection(self, reward: Dict, reason: str):
        """Log rejection for future training"""
        pass
    
    def _adjust_value_model(self, reward: Dict, direction: str):
        """Adjust value prediction model"""
        pass
    
    def _schedule_model_retrain(self):
        """Schedule periodic model retraining"""
        pass
