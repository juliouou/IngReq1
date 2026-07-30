"""Configuracion de la instancia de Celery para SAMR."""
import os
import sys
from pathlib import Path

from celery import Celery

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("samr")

# Toma la configuracion desde settings usando el prefijo CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre automaticamente las tareas definidas en cada app (tasks.py).
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tarea minima de verificacion del worker."""
    print("Celery debug_task ejecutada. Request: {0!r}".format(self.request))
