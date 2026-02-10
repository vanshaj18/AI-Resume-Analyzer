import os
import sys
from pathlib import Path
from celery import Celery

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.setup import broker_url, result_backend

celery_app = Celery(
    "ai_resume_analyzer",
    broker=broker_url,
    backend=result_backend,
    include=["analysis.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_prefetch_multiplier=1,
    worker_concurrency=int(os.getenv("CELERY_CONCURRENCY", "2")),
    task_acks_late=True,
    # --- Time handling ---
    enable_utc=True,
    timezone="UTC",

    # --- Visibility (CRITICAL for long tasks) ---
    broker_transport_options={
        "visibility_timeout": 60 * 60,  # 1 hour
    },
)

celery_app.conf.task_default_queue = "analysis"

celery_app.conf.task_routes = {
    "analysis.tasks.extract_text_task": {"queue": "extraction"},
    "analysis.tasks.analyze_resume_task": {"queue": "analysis"},
    "analysis.tasks.reporting_task": {"queue": "analysis"},
}
