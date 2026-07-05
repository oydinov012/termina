from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator 


# =========================
# PROFILE
# =========================

class Profile(models.Model):

    MAX_LEVEL = 10

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    level = models.PositiveIntegerField(default=1)

    xp = models.PositiveIntegerField(default=0)

    success_streak = models.PositiveIntegerField(default=0)

    failed_attempts = models.PositiveIntegerField(default=0)

    total_completed_tasks = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ["-xp"]

    def __str__(self):

        return f"{self.user.username} | Level {self.level}"


# =========================
# TASK CATEGORY
# =========================

class TaskCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        verbose_name_plural = "Task Categories"

        ordering = ["name"]

    def __str__(self):

        return self.name


# =========================
# TASK TEMPLATE
# =========================

class TaskTemplate(models.Model):

    LEVELS = (
        (1, "Beginner"),
        (2, "Intermediate"),
        (3, "Advanced"),
    )

    TYPES = (
        ("folder", "Folder"),
        ("file", "File"),
        ("mixed", "Mixed"),
        ("nested", "Nested"),
        ("command", "Command"),
    )

    DIFFICULTIES = (
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    target_structure = models.JSONField()

    command = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    expected_output = models.TextField(
        blank=True,
        null=True
    )

    level = models.PositiveIntegerField(
        choices=LEVELS
    )

    type = models.CharField(
        max_length=20,
        choices=TYPES
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTIES,
        default="easy"
    )

    xp = models.IntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    time_limit = models.PositiveIntegerField(
        default=300,
        help_text="Seconds"
    )

    categories = models.ManyToManyField(
        TaskCategory,
        related_name="task_templates"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["level", "xp"]

    def __str__(self):

        return f"{self.title} | Level {self.level}"


# =========================
# GENERATED TASK
# =========================

class Task(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_tasks"
    )

    level = models.PositiveIntegerField()

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    target_structure = models.JSONField()

    xp = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    attempt_count = models.PositiveIntegerField(
        default=0
    )

    execution_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Seconds"
    )

    class Meta:

        ordering = ["-started_at"]

    def __str__(self):

        return f"{self.user.username} - {self.title}"


# =========================
# COMMAND HISTORY
# =========================

class CommandHistory(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="commands"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="command_history"
    )

    command = models.TextField()

    output = models.TextField(
        blank=True,
        null=True
    )

    is_success = models.BooleanField(
        default=True
    )

    executed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-executed_at"]

    def __str__(self):

        return f"{self.user.username} | {self.command}"