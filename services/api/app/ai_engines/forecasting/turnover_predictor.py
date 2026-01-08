"""
Employee Turnover Prediction
Predicts probability of employee leaving
Uses Gradient Boosting Classifier
"""

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TurnoverPredictor:
    """
    Predicts employee turnover risk
    
    Features:
    - Tenure (days)
    - Satisfaction score
    - Last promotion (days ago)
    - Salary percentile
    - Performance score
    - Absences per month
    - Overtime hours per week
    - Department
    - Reports to
    
    Target: Will leave in next 90 days (0/1)
    """
    
    def __init__(self, model_path=None):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        if model_path:
            self.load_model(model_path)
    
    def prepare_features(self, employee_data):
        """Prepare features from employee data"""
        features = []
        
        # Tenure in days
        hire_date = employee_data.get('hire_date')
        if hire_date:
            tenure = (datetime.now() - hire_date).days
        else:
            tenure = 365
        features.append(tenure)
        
        # Satisfaction (0-100)
        features.append(employee_data.get('satisfaction_score', 70))
        
        # Days since last promotion
        last_promotion = employee_data.get('last_promotion_date')
        if last_promotion:
            days_since_promotion = (datetime.now() - last_promotion).days
        else:
            days_since_promotion = tenure
        features.append(days_since_promotion)
        
        # Salary percentile within company
        features.append(employee_data.get('salary_percentile', 50))
        
        # Performance score
        features.append(employee_data.get('performance_score', 75))
        
        # Absences per month
        features.append(employee_data.get('absences_per_month', 1.0))
        
        # Overtime hours per week
        features.append(employee_data.get('overtime_hours_per_week', 3.0))
        
        # Department encoding
        dept = employee_data.get('department', 'other')
        features.append(1 if dept == 'engineering' else 0)
        features.append(1 if dept == 'sales' else 0)
        
        # Manager quality score
        features.append(employee_data.get('manager_quality_score', 75))
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data):
        """Train the turnover prediction model"""
        logger.info(f"Training turnover model with {len(training_data)} samples")
        
        X = []
        y = []
        
        for record in training_data:
            features = self.prepare_features(record)
            X.append(features[0])
            y.append(1 if record['left_within_90_days'] else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Evaluate
        score = self.model.score(X_scaled, y)
        logger.info(f"Training complete - Accuracy: {score:.3f}")
        
        return {'accuracy': score}
    
    def predict_risk(self, employee_data):
        """
        Predict turnover risk
        
        Returns:
            Dict with risk_score (0-100) and risk_level
        """
        features = self.prepare_features(employee_data)
        features_scaled = self.scaler.transform(features)
        
        # Get probability of leaving
        prob = self.model.predict_proba(features_scaled)[0][1]
        risk_score = float(prob * 100)
        
        # Categorize risk
        if risk_score < 20:
            risk_level = 'low'
        elif risk_score < 50:
            risk_level = 'medium'
        elif risk_score < 75:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'probability': float(prob)
        }
    
    def save_model(self, path):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        logger.info(f"Model loaded from {path}")

# Global instance
turnover_predictor = TurnoverPredictor()
