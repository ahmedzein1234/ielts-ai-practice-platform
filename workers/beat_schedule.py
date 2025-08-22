"""Celery Beat schedule configuration for periodic tasks."""

from celery.schedules import crontab
from workers.celery_app import celery_app
from workers.tasks.scoring import cleanup_old_results_task
from workers.tasks.email import send_weekly_report_task
from workers.tasks.file_processing import cleanup_temp_files_task
from workers.tasks.analytics import cleanup_old_analytics_task, generate_weekly_report_task


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Daily cleanup tasks
    'cleanup-old-results-daily': {
        'task': 'workers.tasks.scoring.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'args': (30,),  # Clean up results older than 30 days
    },
    
    'cleanup-temp-files-daily': {
        'task': 'workers.tasks.file_processing.cleanup_temp_files',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
        'args': (24,),  # Clean up files older than 24 hours
    },
    
    'cleanup-old-analytics-daily': {
        'task': 'workers.tasks.analytics.cleanup_old_analytics',
        'schedule': crontab(hour=4, minute=0),  # 4 AM daily
        'args': (90,),  # Clean up analytics older than 90 days
    },
    
    # Weekly tasks
    'generate-weekly-reports': {
        'task': 'workers.tasks.analytics.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
        'args': ({'type': 'platform'},),  # Platform weekly report
    },
    
    'send-weekly-reports': {
        'task': 'workers.tasks.email.send_weekly_report',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
        'args': ({'type': 'platform'},),  # Send platform weekly report
    },
    
    # Hourly health checks (optional)
    'health-check-hourly': {
        'task': 'workers.tasks.health.health_check',
        'schedule': crontab(minute=0),  # Every hour
        'args': (),
    },
}

# Enable timezone support
celery_app.conf.enable_utc = True
celery_app.conf.timezone = 'UTC'
