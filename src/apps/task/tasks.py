import os
import random
from django.utils import timezone

from .models import (
    Task,
    Profile,
    TaskTemplate,
)


# =========================
# TASK ENGINE
# =========================
class TaskEngine:

    @staticmethod
    def generate(user):

        profile, _ = Profile.objects.get_or_create(user=user)
        level = profile.level

        templates = TaskTemplate.objects.filter(
            level=level,
            is_active=True
        )

        if not templates.exists():
            templates = TaskTemplate.objects.filter(
                level=1,
                is_active=True
            )

        templates = list(templates)

        if not templates:
            raise ValueError("No TaskTemplate found")

        template = random.choice(templates)

        return Task.objects.create(
            user=user,
            template=template,
            level=template.level,
            title=template.title,
            description=template.description,
            target_structure=template.target_structure,  # <-- shu yerga e'tibor
            xp=template.xp,
        )
# =========================
# TASK CHECKER
# =========================

class TaskChecker:

    @staticmethod
    def check(workspace, task):

        base_path = workspace.current_dir

        target_structure = task.target_structure

        return TaskChecker._check_structure(
            base_path,
            target_structure
        )

    @staticmethod
    def _check_structure(base_path, structure):

        for name, content in structure.items():

            path = os.path.join(base_path, name)

            # =========================
            # FILE
            # =========================

            if content is None:

                if not os.path.isfile(path):
                    return False

            # =========================
            # EMPTY FOLDER
            # =========================

            elif isinstance(content, dict) and not content:

                if not os.path.isdir(path):
                    return False

            # =========================
            # NESTED FOLDER
            # =========================

            elif isinstance(content, dict):

                if not os.path.isdir(path):
                    return False

                nested_check = TaskChecker._check_structure(
                    path,
                    content
                )

                if not nested_check:
                    return False

        return True


# =========================
# PROGRESS MANAGER
# =========================

class ProgressManager:

    LEVEL_UP_STREAK = 5

    @staticmethod
    def update(user, task, success):

        profile = user.profile

        task.attempt_count += 1

        if success:

            task.status = "completed"

            task.completed_at = timezone.now()

            profile.xp += task.xp

            profile.success_streak += 1

            profile.total_completed_tasks += 1

            # level up
            if (
                profile.success_streak >=
                ProgressManager.LEVEL_UP_STREAK
            ):

                if profile.level < Profile.MAX_LEVEL:

                    profile.level += 1

                profile.success_streak = 0

        else:

            task.status = "failed"

            profile.failed_attempts += 1

            profile.success_streak = 0

        profile.save()

        task.save()


# =========================
# TASK FORMATTER
# =========================

class TaskFormatter:

    @staticmethod
    def format_structure(structure, indent=0):

        result = []

        for name, content in structure.items():

            prefix = "  " * indent

            # =========================
            # FILE
            # =========================

            if content is None:

                result.append(
                    f"{prefix}📄 {name}"
                )

            # =========================
            # EMPTY FOLDER
            # =========================

            elif isinstance(content, dict) and not content:

                result.append(
                    f"{prefix}📁 {name}"
                )

            # =========================
            # NESTED FOLDER
            # =========================

            elif isinstance(content, dict):

                result.append(
                    f"{prefix}📁 {name}"
                )

                result.extend(
                    TaskFormatter.format_structure(
                        content,
                        indent + 1
                    )
                )

        return result

    @staticmethod
    def to_text(structure):

        lines = TaskFormatter.format_structure(
            structure
        )

        return "\n".join(lines)