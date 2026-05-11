from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    level = models.IntegerField(default=1)

    xp = models.IntegerField(default=0)

    success_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} (L{self.level})"
    
class Task(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    level = models.IntegerField()

    title = models.CharField(max_length=255)

    description = models.TextField()

    target_structure = models.JSONField()

    xp = models.IntegerField(default=1)

    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)