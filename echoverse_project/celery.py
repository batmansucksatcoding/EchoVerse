# echoverse_project/celery.py
import os
import socket
from celery import Celery
from celery.schedules import crontab

# ==========================================
# Detect Redis before initializing Celery
# ==========================================
def redis_available(host="127.0.0.1", port=6379):
    try:
        sock = socket.create_connection((host, port), timeout=1)
        sock.close()
        return True
    except OSError:
        return False


# ==========================================
# Set environment before Celery reads Django settings
# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echoverse_project.settings')

# Choose broker *before* app initialization
if redis_available():
    broker_url = "redis://127.0.0.1:6379/0"
    result_backend = "redis://127.0.0.1:6379/0"
    eager = False
    print("✅ Redis detected — background task mode enabled.")
else:
    broker_url = "memory://"
    result_backend = "cache+memory://"
    eager = True
    print("⚠️ Redis not detected — instant (eager) mode active.")


# ==========================================
# Initialize Celery with correct broker/backend
# ==========================================
app = Celery("echoverse_project", broker=broker_url, backend=result_backend)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Force eager mode if offline
if eager:
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

# ==========================================
# Scheduled (beat) tasks
# ==========================================
app.conf.beat_schedule = {
    "generate-weekly-summaries": {
        "task": "journal.tasks.generate_weekly_summaries",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),
    },
    "generate-monthly-letters": {
        "task": "journal.tasks.generate_monthly_letters",
        "schedule": crontab(day_of_month=1, hour=10, minute=0),
    },
}
