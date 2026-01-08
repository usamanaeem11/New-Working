"""
Celery Background Workers
Handles asynchronous tasks: emails, reports, AI processing
"""

from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery
celery_app = Celery(
    'workingtracker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    include=[
        'app.workers.tasks.email_tasks',
        'app.workers.tasks.report_tasks',
        'app.workers.tasks.ai_tasks',
        'app.workers.tasks.payroll_tasks',
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks (cron jobs)
celery_app.conf.beat_schedule = {
    'generate-daily-reports': {
        'task': 'app.workers.tasks.report_tasks.generate_daily_reports',
        'schedule': crontab(hour=6, minute=0),  # 6 AM daily
    },
    'run-weekly-payroll': {
        'task': 'app.workers.tasks.payroll_tasks.run_weekly_payroll',
        'schedule': crontab(day_of_week=5, hour=14, minute=0),  # Friday 2 PM
    },
    'train-ai-models': {
        'task': 'app.workers.tasks.ai_tasks.train_models_weekly',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
    },
    'cleanup-old-sessions': {
        'task': 'app.workers.tasks.maintenance_tasks.cleanup_expired_sessions',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}

if __name__ == '__main__':
    celery_app.start()
