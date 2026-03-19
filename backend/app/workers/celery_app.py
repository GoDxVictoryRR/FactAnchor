from celery import Celery
import os
import logging

logger = logging.getLogger(__name__)

# Note: In a full app, these would come from app.config.settings
# Fetch URLs from environment
# We prioritize DATABASE_URL for the backend if REDIS_URL is missing
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
BROKER_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")

# Scrub any Render-injected Redis variables to prevent Celery from dynamically overriding the backend
for key in ["CELERY_RESULT_BACKEND", "REDIS_URL", "CELERY_BROKER_URL"]:
    if key in os.environ and "redis" in os.environ.get(key, ""):
        os.environ.pop(key, None)

# For the result backend, we use the database to avoid Redis dependency on Render free tier.
# We FORCE use the database URL to override any misconfigured environment variables.
# Safely handle various Postgres schemes (postgresql://, postgres://, postgresql+asyncpg://)
import re
RESULT_BACKEND = re.sub(r"^postgres(?:ql)?(?:\+.*?)*://", "db+postgresql://", DATABASE_URL)

# Ensure we don't have multiple prefixes
RESULT_BACKEND = RESULT_BACKEND.replace("db+db+", "db+")

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
