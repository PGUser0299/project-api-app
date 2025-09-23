import os
import multiprocessing
from celery import Celery
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


multiprocessing.set_start_method("spawn", True)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

