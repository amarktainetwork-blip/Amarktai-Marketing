"""
Celery Configuration for Amarktai Marketing
"""

from celery import Celery
from celery.signals import beat_init
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "amarktai_marketing",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=86400,  # Results expire after 24 hours
)

# Beat schedule - periodic tasks
celery_app.conf.beat_schedule = {
    # Nightly content generation at 2:00 AM UTC
    "nightly-content-generation": {
        "task": "app.workers.tasks.run_nightly_content_generation",
        "schedule": crontab(hour=2, minute=0),
    },
    
    # Sync platform analytics every 6 hours
    "sync-analytics": {
        "task": "app.workers.tasks.sync_platform_analytics",
        "schedule": crontab(hour="*/6", minute=0),
    },
    
    # Fetch platform engagement every 30 minutes
    "fetch-engagement": {
        "task": "app.workers.tasks.fetch_platform_engagement",
        "schedule": crontab(minute="*/30"),
    },
    
    # Analyze A/B tests daily at 3:00 AM
    "analyze-ab-tests": {
        "task": "app.workers.tasks.analyze_ab_tests",
        "schedule": crontab(hour=3, minute=0),
    },
    
    # Post scheduled content every 15 minutes
    "post-scheduled-content": {
        "task": "app.workers.tasks.schedule_posts_worker",
        "schedule": crontab(minute="*/15"),
    },
}

@beat_init.connect
def on_beat_init(sender, **kwargs):
    """Called when Celery beat starts."""
    print("🕐 Celery beat scheduler initialized")
    print("📅 Scheduled tasks:")
    for task_name, schedule in celery_app.conf.beat_schedule.items():
        print(f"  - {task_name}: {schedule['schedule']}")

# Task success/failure handlers
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")
    return {"status": "ok"}

if __name__ == "__main__":
    celery_app.start()
