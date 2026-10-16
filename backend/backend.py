
import os
import signal
import subprocess
import sys
import time


processes = []


def shutdown(signum, frame):
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()

    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

processes.append(
    subprocess.Popen([
        "celery",
        "-A",
        "app.tasks.celery_app:celery_app",
        "worker",
        "--loglevel=info",
        "--pool=solo",
        "--concurrency=1",
    ])
)

processes.append(
    subprocess.Popen([
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        os.getenv("PORT", "8000"),
    ])
)

try:
    while True:
        for process in processes:
            if process.poll() is not None:
                shutdown(signal.SIGTERM, None)

        time.sleep(1)
finally:
    shutdown(signal.SIGTERM, None)
