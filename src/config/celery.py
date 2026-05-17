# config/celery.py

import os
from celery import Celery

# Django sozlamalarini Celery uchun biriktiramiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Barcha Celery konfiguratsiyalarini settings.py ichidan 'CELERY_' prefiksi orqali o'qiymiz
app.config_from_object('django.conf:settings', namespace='CELERY')

# Loyihadagi barcha app-lar ichidagi tasks.py fayllarini avtomatik qidirib topadi
app.autodiscover_tasks()