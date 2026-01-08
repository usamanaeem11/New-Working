"""
Reward Engine - Core reward processing system
Handles both manual and AI-powered rewards
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class RewardType(Enum):
    BADGE = "badge"
    POINTS = "points"
    BONUS = "bonus"
    ACHIEVEMENT = "achievement"

class RewardSource(Enum):
    MANUAL = "manual"           # Awarded by manager/admin
    AI_AUTO = "ai_auto"         # AI auto-awarded
    AI_SUGGESTED = "ai_suggested"  # AI suggested, pending approval

class RewardEngine:
    """Core reward processing engine"""
    
    def __init__(self, db_session, ai_engine):
        self.db = db_session
        self.ai = ai_engine
        
    # ========== MANUAL REWARDS ==========
    
    def award_badge_manual(
        self,
        employee_id: str,
        badge_id: str,
        awarded_by: str,
        reason: str
    ) -> Dict:
        """
        Manager/Admin manually awards a badge
        
        Args:
            employee_id: Employee receiving badge
            badge_id: Badge type
            awarded_by: Manager/Admin ID
            reason: Why badge is awarded
        """
        badge = {
            'id': self._generate_id(),
            'employee_id': employee_id,
            'badge_id': badge_id,
            'type': RewardType.BADGE.value,
            'source': RewardSource.MANUAL.value,
            'awarded_by': awarded_by,
            'reason': reason,
            'awarded_at': datetime.utcnow().isoformat(),
            'points_value': self._get_badge_points(badge_id)
        }
        
        # Save to database
        self.db.save_reward(badge)
        
        # Update employee points
        self._update_points(employee_id, badge['points_value'])
        
        # Send notification
        self._notify_employee(employee_id, badge)
        
        return badge
    
    def award_bonus_manual(
        self,
        employee_id: str,
        amount: float,
        awarded_by: str,
        reason: str,
        bonus_type: str = "performance"
    ) -> Dict:
        """
        Manager/Admin manually awards a monetary bonus
        
        Args:
            employee_id: Employee receiving bonus
            amount: Bonus amount ($)
            awarded_by: Manager/Admin ID
            reason: Why bonus is awarded
            bonus_type: Type (performance, project, special)
        """
        bonus = {
            'id': self._generate_id(),
            'employee_id': employee_id,
            'type': RewardType.BONUS.value,
            'source': RewardSource.MANUAL.value,
            'amount': amount,
            'bonus_type': bonus_type,
            'awarded_by': awarded_by,
            'reason': reason,
            'awarded_at': datetime.utcnow().isoformat(),
            'status': 'approved'
        }
        
        # Save to database
        self.db.save_reward(bonus)
        
        # Notify payroll system
        self._notify_payroll(bonus)
        
        # Send notification
        self._notify_employee(employee_id, bonus)
        
        return bonus
    
    def award_points_manual(
        self,
        employee_id: str,
        points: int,
        awarded_by: str,
        reason: str
    ) -> Dict:
        """Manager/Admin manually awards points"""
        reward = {
            'id': self._generate_id(),
            'employee_id': employee_id,
            'type': RewardType.POINTS.value,
            'source': RewardSource.MANUAL.value,
            'points': points,
            'awarded_by': awarded_by,
            'reason': reason,
            'awarded_at': datetime.utcnow().isoformat()
        }
        
        self.db.save_reward(reward)
        self._update_points(employee_id, points)
        self._notify_employee(employee_id, reward)
        
        return reward
    
    # ========== AI-POWERED REWARDS ==========
    
    def detect_reward_opportunities(self, employee_id: str) -> List[Dict]:
        """
        AI detects reward opportunities for an employee
        
        Returns list of suggested rewards with:
        - What reward
        - Why (AI reasoning)
        - Confidence score
        - Auto-award eligible?
        """
        # Get employee data
        employee = self.db.get_employee(employee_id)
        metrics = self.db.get_employee_metrics(employee_id)
        
        # AI analyzes data
        opportunities = self.ai.analyze_reward_opportunities(
            employee=employee,
            metrics=metrics,
            history=self.db.get_reward_history(employee_id)
        )
        
        return opportunities
    
    def award_ai_suggested(self, opportunity_id: str) -> Dict:
        """
        AI suggests reward, requires manager approval
        
        Creates pending reward that manager must approve
        """
        opportunity = self.db.get_opportunity(opportunity_id)
        
        suggested_reward = {
            'id': self._generate_id(),
            'employee_id': opportunity['employee_id'],
            'type': opportunity['reward_type'],
            'source': RewardSource.AI_SUGGESTED.value,
            'ai_reasoning': opportunity['reasoning'],
            'ai_confidence': opportunity['confidence'],
            'suggested_at': datetime.utcnow().isoformat(),
            'status': 'pending_approval',
            'suggested_value': opportunity['value']
        }
        
        self.db.save_suggested_reward(suggested_reward)
        
        # Notify manager for approval
        self._notify_manager_for_approval(
            opportunity['employee_id'],
            suggested_reward
        )
        
        return suggested_reward
    
    def award_ai_auto(self, employee_id: str, trigger: str) -> Optional[Dict]:
        """
        AI automatically awards reward (no approval needed)
        
        Only for low-value rewards and high-confidence triggers
        
        Args:
            employee_id: Employee ID
            trigger: What triggered the reward (e.g., "perfect_attendance_7_days")
        """
        # Get auto-award rules
        rules = self.db.get_auto_award_rules()
        
        # Check if this trigger qualifies for auto-award
        if not self._qualifies_for_auto_award(trigger, rules):
            return None
        
        # AI validates
        validation = self.ai.validate_auto_award(employee_id, trigger)
        
        if not validation['approved']:
            return None
        
        # Auto-award
        reward = {
            'id': self._generate_id(),
            'employee_id': employee_id,
            'type': validation['reward_type'],
            'source': RewardSource.AI_AUTO.value,
            'trigger': trigger,
            'ai_reasoning': validation['reasoning'],
            'value': validation['value'],
            'awarded_at': datetime.utcnow().isoformat(),
            'status': 'auto_approved'
        }
        
        self.db.save_reward(reward)
        
        # Update points/bonus
        if reward['type'] == RewardType.POINTS.value:
            self._update_points(employee_id, reward['value'])
        
        # Notify employee
        self._notify_employee(employee_id, reward)
        
        return reward
    
    # ========== MANAGER ACTIONS ==========
    
    def approve_suggested_reward(self, reward_id: str, manager_id: str) -> Dict:
        """Manager approves AI-suggested reward"""
        reward = self.db.get_reward(reward_id)
        
        if reward['status'] != 'pending_approval':
            raise ValueError("Reward not pending approval")
        
        # Update status
        reward['status'] = 'approved'
        reward['approved_by'] = manager_id
        reward['approved_at'] = datetime.utcnow().isoformat()
        
        self.db.update_reward(reward)
        
        # Process reward
        self._process_approved_reward(reward)
        
        return reward
    
    def reject_suggested_reward(
        self,
        reward_id: str,
        manager_id: str,
        reason: str
    ) -> Dict:
        """Manager rejects AI-suggested reward"""
        reward = self.db.get_reward(reward_id)
        
        reward['status'] = 'rejected'
        reward['rejected_by'] = manager_id
        reward['rejected_at'] = datetime.utcnow().isoformat()
        reward['rejection_reason'] = reason
        
        self.db.update_reward(reward)
        
        # Learn from rejection (improve AI)
        self.ai.learn_from_rejection(reward, reason)
        
        return reward
    
    # ========== BADGE DEFINITIONS ==========
    
    def get_available_badges(self) -> List[Dict]:
        """Get all available badges"""
        return [
            # Attendance Badges
            {
                'id': 'perfect_attendance_week',
                'name': 'Perfect Week',
                'description': 'No missed days for 7 consecutive days',
                'category': 'attendance',
                'points': 50,
                'icon': '🎯'
            },
            {
                'id': 'perfect_attendance_month',
                'name': 'Perfect Month',
                'description': 'No missed days for 30 consecutive days',
                'category': 'attendance',
                'points': 200,
                'icon': '⭐'
            },
            {
                'id': 'early_bird',
                'name': 'Early Bird',
                'description': 'Arrive early 20 times',
                'category': 'punctuality',
                'points': 100,
                'icon': '🌅'
            },
            
            # Performance Badges
            {
                'id': 'top_performer',
                'name': 'Top Performer',
                'description': 'Top 10% productivity this month',
                'category': 'performance',
                'points': 500,
                'icon': '🏆'
            },
            {
                'id': 'task_master',
                'name': 'Task Master',
                'description': 'Complete 100 tasks',
                'category': 'productivity',
                'points': 300,
                'icon': '✅'
            },
            
            # Collaboration Badges
            {
                'id': 'team_player',
                'name': 'Team Player',
                'description': 'Help 10 team members',
                'category': 'collaboration',
                'points': 150,
                'icon': '🤝'
            },
            {
                'id': 'mentor',
                'name': 'Mentor',
                'description': 'Mentor 3 employees',
                'category': 'leadership',
                'points': 250,
                'icon': '👨‍🏫'
            },
            
            # Cognitive Health Badges (AI-powered)
            {
                'id': 'burnout_avoider',
                'name': 'Burnout Avoider',
                'description': 'Maintain low burnout risk for 30 days',
                'category': 'wellness',
                'points': 200,
                'icon': '🧘'
            },
            {
                'id': 'focus_master',
                'name': 'Focus Master',
                'description': 'High focus score for 7 consecutive days',
                'category': 'cognitive',
                'points': 150,
                'icon': '🎯'
            },
            {
                'id': 'flow_state_expert',
                'name': 'Flow State Expert',
                'description': 'Achieve flow state 20 times',
                'category': 'cognitive',
                'points': 300,
                'icon': '🌊'
            },
            
            # Special Badges
            {
                'id': 'innovator',
                'name': 'Innovator',
                'description': 'Submit innovative idea',
                'category': 'innovation',
                'points': 250,
                'icon': '💡'
            },
            {
                'id': 'first_timer',
                'name': 'First Timer',
                'description': 'Complete first task',
                'category': 'milestone',
                'points': 10,
                'icon': '🎈'
            }
        ]
    
    # ========== HELPER METHODS ==========
    
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _get_badge_points(self, badge_id: str) -> int:
        badges = {b['id']: b['points'] for b in self.get_available_badges()}
        return badges.get(badge_id, 0)
    
    def _update_points(self, employee_id: str, points: int):
        """Update employee point balance"""
        current = self.db.get_employee_points(employee_id)
        new_total = current + points
        self.db.update_employee_points(employee_id, new_total)
    
    def _notify_employee(self, employee_id: str, reward: Dict):
        """Send notification to employee"""
        # Send push notification, email, in-app notification
        pass
    
    def _notify_manager_for_approval(self, employee_id: str, reward: Dict):
        """Notify manager about pending reward"""
        pass
    
    def _notify_payroll(self, bonus: Dict):
        """Notify payroll system about bonus"""
        pass
    
    def _qualifies_for_auto_award(self, trigger: str, rules: List) -> bool:
        """Check if trigger qualifies for auto-award"""
        return trigger in [r['trigger'] for r in rules if r['auto_approve']]
    
    def _process_approved_reward(self, reward: Dict):
        """Process approved reward"""
        if reward['type'] == RewardType.POINTS.value:
            self._update_points(reward['employee_id'], reward['suggested_value'])
        elif reward['type'] == RewardType.BONUS.value:
            self._notify_payroll(reward)
        
        self._notify_employee(reward['employee_id'], reward)
