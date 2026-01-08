"""
AI Data Validation
No training without validation pass - ENFORCED
"""

import pandas as pd
import hashlib
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates training data before AI processing
    Ensures data quality and compliance
    """
    
    def __init__(self):
        self.validation_history = []
    
    def validate_training_data(
        self,
        data: List[Dict[str, Any]],
        schema: Dict[str, Any]
    ) -> Tuple[bool, List[str], str]:
        """
        Comprehensive validation of training data
        
        Args:
            data: Training dataset
            schema: Expected schema definition
            
        Returns:
            (is_valid, errors, dataset_hash)
        """
        
        errors = []
        
        # Convert to DataFrame
        try:
            df = pd.DataFrame(data)
        except Exception as e:
            return False, [f"Data conversion failed: {e}"], None
        
        # Validation 1: Schema compliance
        schema_errors = self._validate_schema(df, schema)
        errors.extend(schema_errors)
        
        # Validation 2: Missing values
        missing_errors = self._check_missing_values(df)
        errors.extend(missing_errors)
        
        # Validation 3: Data ranges
        range_errors = self._check_ranges(df, schema)
        errors.extend(range_errors)
        
        # Validation 4: Data types
        type_errors = self._check_types(df, schema)
        errors.extend(type_errors)
        
        # Validation 5: PII detection
        pii_errors = self._detect_pii(df)
        errors.extend(pii_errors)
        
        # Validation 6: Statistical anomalies
        anomaly_errors = self._check_anomalies(df)
        errors.extend(anomaly_errors)
        
        # Generate dataset hash (immutable ID)
        dataset_hash = self._generate_hash(data)
        
        # Log validation
        is_valid = len(errors) == 0
        self._log_validation(is_valid, errors, dataset_hash)
        
        return is_valid, errors, dataset_hash
    
    def _validate_schema(self, df: pd.DataFrame, schema: Dict) -> List[str]:
        """Validate column schema"""
        errors = []
        
        required_columns = schema.get('required_columns', [])
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        return errors
    
    def _check_missing_values(self, df: pd.DataFrame) -> List[str]:
        """Check for missing values"""
        errors = []
        
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                pct = (count / len(df)) * 100
                if pct > 10:  # More than 10% missing
                    errors.append(f"Column {col} has {pct:.1f}% missing values")
        
        return errors
    
    def _check_ranges(self, df: pd.DataFrame, schema: Dict) -> List[str]:
        """Validate data ranges"""
        errors = []
        
        ranges = schema.get('ranges', {})
        for col, (min_val, max_val) in ranges.items():
            if col in df.columns:
                if df[col].min() < min_val:
                    errors.append(f"{col} has values below minimum {min_val}")
                if df[col].max() > max_val:
                    errors.append(f"{col} has values above maximum {max_val}")
        
        return errors
    
    def _check_types(self, df: pd.DataFrame, schema: Dict) -> List[str]:
        """Validate data types"""
        errors = []
        
        expected_types = schema.get('types', {})
        for col, expected_type in expected_types.items():
            if col in df.columns:
                if df[col].dtype != expected_type:
                    errors.append(
                        f"{col} has type {df[col].dtype}, expected {expected_type}"
                    )
        
        return errors
    
    def _detect_pii(self, df: pd.DataFrame) -> List[str]:
        """Detect PII in dataset"""
        errors = []
        
        # Check column names for PII indicators
        pii_keywords = ['ssn', 'social', 'credit', 'password', 'secret']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in pii_keywords):
                errors.append(f"Potential PII detected in column: {col}")
        
        return errors
    
    def _check_anomalies(self, df: pd.DataFrame) -> List[str]:
        """Check for statistical anomalies"""
        errors = []
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            # Check for outliers using IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            outliers = df[(df[col] < (Q1 - 3 * IQR)) | (df[col] > (Q3 + 3 * IQR))]
            
            if len(outliers) > len(df) * 0.05:  # More than 5% outliers
                errors.append(
                    f"{col} has {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)"
                )
        
        return errors
    
    def _generate_hash(self, data: List[Dict]) -> str:
        """Generate immutable dataset hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _log_validation(self, is_valid: bool, errors: List[str], dataset_hash: str):
        """Log validation results"""
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'is_valid': is_valid,
            'errors': errors,
            'dataset_hash': dataset_hash
        }
        
        self.validation_history.append(result)
        
        if is_valid:
            logger.info(f"Data validation passed: {dataset_hash}")
        else:
            logger.error(f"Data validation failed: {errors}")

# Global instance
data_validator = DataValidator()
