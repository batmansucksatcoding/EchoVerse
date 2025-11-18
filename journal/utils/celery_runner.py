from django.conf import settings

def run_task_safely(task_func, *args, **kwargs):
    """
    Universal helper to safely run Celery tasks.
    - If Celery is in eager (offline) mode -> run task immediately.
    - If Redis is online -> queue task asynchronously.
    """
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        print(f"⚡ Running {task_func.__name__} instantly (eager mode)")
        return task_func(*args, **kwargs)
    else:
        print(f"🔁 Queuing {task_func.__name__} (Celery background mode)")
        return task_func.delay(*args, **kwargs)
