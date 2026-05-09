import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from .models import Workspace

@receiver(post_save, sender=User)
def create_user_workspace(sender, instance, created, **kwargs):
    if created:
        # Papka yo'li: settings.BASE_DIR/workspaces/user_1_admin
        folder_name = f"user_{instance.id}_{instance.username}"
        path = os.path.join(settings.BASE_DIR, 'workspaces', folder_name)
        
        os.makedirs(path, exist_ok=True)
        
        Workspace.objects.create(
            user=instance,
            root_dir=path,
            current_dir=path
        )