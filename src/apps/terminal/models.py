from django.db import models
from django.contrib.auth.models import User

class Workspace(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='workspace')
    root_dir = models.CharField(max_length=500, blank=True)
    current_dir = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.current_dir}"
    
    