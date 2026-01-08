"""
Centralized Logging Configuration
Structured logging with multiple handlers
Supports: Console, File, Elasticsearch, CloudWatch
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    Outputs logs in JSON format for easy parsing
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'tenant_id'):
            log_data['tenant_id'] = record.tenant_id
        
        return json.dumps(log_data)

def setup_logging(
    log_level: str = 'INFO',
    log_file: str = 'logs/workingtracker.log',
    enable_json: bool = True
) -> None:
    """
    Setup centralized logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        enable_json: Use JSON formatting
    """
    
    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (JSON for parsing)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    
    if enable_json:
        file_handler.setFormatter(JSONFormatter())
    else:
        file_handler.setFormatter(console_formatter)
    
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=50 * 1024 * 1024,  # 50 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter() if enable_json else console_formatter)
    root_logger.addHandler(error_handler)
    
    # Audit log handler (separate file for security events)
    audit_handler = logging.handlers.RotatingFileHandler(
        'logs/audit.log',
        maxBytes=50 * 1024 * 1024,
        backupCount=20  # Keep more audit logs
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(JSONFormatter())
    
    # Only attach to audit logger
    audit_logger = logging.getLogger('audit')
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    logging.info(f"Logging configured: level={log_level}, file={log_file}")

def log_audit_event(
    event_type: str,
    user_id: int = None,
    tenant_id: int = None,
    resource: str = None,
    action: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log security audit event
    
    Args:
        event_type: Type of event (auth, data_access, config_change)
        user_id: User performing action
        tenant_id: Tenant context
        resource: Resource being accessed
        action: Action being performed
        details: Additional details
    """
    audit_logger = logging.getLogger('audit')
    
    event_data = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'tenant_id': tenant_id,
        'resource': resource,
        'action': action,
        'details': details or {}
    }
    
    audit_logger.info(
        f"AUDIT: {event_type}",
        extra={
            'user_id': user_id,
            'tenant_id': tenant_id,
            'audit_data': event_data
        }
    )

# Initialize logging on import
setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', 'logs/workingtracker.log'),
    enable_json=os.getenv('LOG_FORMAT', 'json') == 'json'
)
