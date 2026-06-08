
from django.apps import AppConfig

class TaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.task'

    def ready(self):
        # Signalni tizimga ulash uning ready() metodi ichida import qilinadi
        import apps.task.signals