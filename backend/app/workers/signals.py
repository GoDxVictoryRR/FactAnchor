import logging
from celery.signals import task_success, task_failure

logger = logging.getLogger(__name__)


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    logger.info(f"Task {sender.name} completed successfully: {result}")


@task_failure.connect
def task_failure_handler(sender=None, exception=None, traceback=None, **kwargs):
    logger.error(f"Task {sender.name} failed: {exception}", exc_info=True)
