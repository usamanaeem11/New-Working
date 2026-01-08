"""
Performance Prediction Model
Predicts employee performance based on historical data
Uses Random Forest Regressor
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PerformancePredictor:
    """
    ML model for predicting employee performance
    
    Features:
    - Hours worked per week
    - Task completion rate
    - Average task duration
    - Attendance rate
    - Overtime hours
    - Days since hire
    - Department encoding
    - Role encoding
    
    Target: Performance score (0-100)
    """
    
    def __init__(self, model_path=None):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'hours_per_week',
            'task_completion_rate',
            'avg_task_duration',
            'attendance_rate',
            'overtime_hours',
            'days_since_hire',
            'dept_engineering',
            'dept_sales',
            'dept_marketing',
            'role_senior',
            'role_junior'
        ]
        
        if model_path:
            self.load_model(model_path)
    
    def prepare_features(self, employee_data):
        """
        Prepare features from employee data
        
        Args:
            employee_data: Dict with employee metrics
            
        Returns:
            numpy array of features
        """
        features = []
        
        # Numerical features
        features.append(employee_data.get('hours_per_week', 40))
        features.append(employee_data.get('task_completion_rate', 0.85))
        features.append(employee_data.get('avg_task_duration', 2.5))
        features.append(employee_data.get('attendance_rate', 0.95))
        features.append(employee_data.get('overtime_hours', 5))
        
        # Days since hire
        hire_date = employee_data.get('hire_date')
        if hire_date:
            days = (datetime.now() - hire_date).days
        else:
            days = 365
        features.append(days)
        
        # One-hot encoded department
        dept = employee_data.get('department', 'other')
        features.append(1 if dept == 'engineering' else 0)
        features.append(1 if dept == 'sales' else 0)
        features.append(1 if dept == 'marketing' else 0)
        
        # One-hot encoded role
        role = employee_data.get('role', 'junior')
        features.append(1 if 'senior' in role.lower() else 0)
        features.append(1 if 'junior' in role.lower() else 0)
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data):
        """
        Train the model on historical data
        
        Args:
            training_data: List of dicts with employee data and scores
        """
        logger.info(f"Training performance model with {len(training_data)} samples")
        
        # Prepare features and targets
        X = []
        y = []
        
        for record in training_data:
            features = self.prepare_features(record)
            X.append(features[0])
            y.append(record['performance_score'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Training complete - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': dict(zip(
                self.feature_names,
                self.model.feature_importances_
            ))
        }
    
    def predict(self, employee_data):
        """
        Predict performance score for an employee
        
        Args:
            employee_data: Dict with employee metrics
            
        Returns:
            Predicted performance score (0-100)
        """
        features = self.prepare_features(employee_data)
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        
        # Clip to valid range
        prediction = np.clip(prediction, 0, 100)
        
        return float(prediction)
    
    def predict_batch(self, employees_data):
        """
        Predict performance for multiple employees
        
        Args:
            employees_data: List of employee data dicts
            
        Returns:
            List of predicted scores
        """
        predictions = []
        for employee_data in employees_data:
            prediction = self.predict(employee_data)
            predictions.append(prediction)
        
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        return dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
    
    def save_model(self, path):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        logger.info(f"Model loaded from {path}")

# Global instance
performance_predictor = PerformancePredictor()
