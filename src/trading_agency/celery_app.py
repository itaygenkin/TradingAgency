import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from celery import Celery

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

CELERY_COUNTDOWN = 300  # time in seconds


def _is_docker_environment() -> bool:
    return os.path.exists("/.dockerenv")


def _resolve_redis_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname != "redis" or _is_docker_environment():
        return url

    return urlunparse(parsed._replace(netloc=f"localhost:{parsed.port or 6379}"))


if _is_docker_environment():
    REDIS_URL = _resolve_redis_url(os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"))
    REDIS_BACKEND_URL = _resolve_redis_url(os.getenv("CELERY_RESULT_BACKEND", REDIS_URL))
else:
    REDIS_URL = _resolve_redis_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    REDIS_BACKEND_URL = _resolve_redis_url(os.getenv("REDIS_BACKEND_URL", REDIS_URL))

os.environ["CELERY_BROKER_URL"] = REDIS_URL
os.environ["CELERY_RESULT_BACKEND"] = REDIS_BACKEND_URL

celery_app = Celery(
    "trading_agency",
    broker=REDIS_URL,
    backend=REDIS_BACKEND_URL,
    include=["src.trading_agency.application.celery_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
)
