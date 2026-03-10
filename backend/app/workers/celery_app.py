from celery import Celery
import os
import logging

logger = logging.getLogger(__name__)

# Note: In a full app, these would come from app.config.settings
BROKER_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery(
    "factanchor",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.workers.tasks"]
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.verify_claim": {"queue": "verification"},
        "app.workers.tasks.check_report_complete": {"queue": "verification"},
    }
)

# Optional: Set up beat schedule for periodic tasks
app.conf.beat_schedule = {
    "cleanup-stale-reports": {
        "task": "app.workers.tasks.cleanup_stale_reports",
        "schedule": 86400.0, # Every 24 hours
    },
}

if __name__ == "__main__":
    app.start()
