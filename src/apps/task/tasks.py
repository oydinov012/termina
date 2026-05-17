import os
import random
from django.utils import timezone
from .models import Task, Profile, TaskTemplate

# ==========================================
# 1. TASK ENGINE
# ==========================================
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
            target_structure=template.target_structure,
            xp=template.xp,
            status="created"  # Boshlang'ich holat
        )


# ==========================================
# 2. TASK CHECKER
# ==========================================
class TaskChecker:

    @staticmethod
    def check(workspace_path, task):
        """
        Topshiriq tekshiruvi foydalanuvchining ayni joriy papkasida emas,
        aynan o'sha task uchun ajratilgan maxsus `workspace_path` ichida tekshiriladi.
        """
        return TaskChecker._check_structure(workspace_path, task.target_structure)

    @staticmethod
    def _check_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)

            # ---------------------------
            # FILE (Fayl va uning kontenti)
            # ---------------------------
            if content is None or isinstance(content, str):
                if not os.path.isfile(path):
                    return False

                # Agar kontent string bo'lsa, ichidagi matnni tekshiramiz
                if isinstance(content, str):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            file_content = f.read().strip()
                        
                        if file_content != content.strip():
                            return False
                    except Exception:
                        return False

            # ---------------------------
            # EMPTY FOLDER
            # ---------------------------
            elif isinstance(content, dict) and not content:
                if not os.path.isdir(path):
                    return False

            # ---------------------------
            # NESTED FOLDER
            # ---------------------------
            elif isinstance(content, dict):
                if not os.path.isdir(path):
                    return False

                nested_check = TaskChecker._check_structure(path, content)
                if not nested_check:
                    return False

        return True


# ==========================================
# 3. PROGRESS MANAGER
# ==========================================
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

            if profile.success_streak >= ProgressManager.LEVEL_UP_STREAK:
                if profile.level < Profile.MAX_LEVEL:
                    profile.level += 1
                profile.success_streak = 0
        else:
            task.status = "failed"
            profile.failed_attempts += 1
            profile.success_streak = 0

        profile.save()
        task.save()


# ==========================================
# 4. TASK FORMATTER
# ==========================================
class TaskFormatter:

    @staticmethod
    def format_structure(structure, indent=0):
        result = []

        for name, content in structure.items():
            prefix = "  " * indent

            if content is None or isinstance(content, str):
                if isinstance(content, str):
                    result.append(f"{prefix}📄 {name} (kontent: '{content}')")
                else:
                    result.append(f"{prefix}📄 {name}")

            elif isinstance(content, dict) and not content:
                result.append(f"{prefix}📁 {name}")

            elif isinstance(content, dict):
                result.append(f"{prefix}📁 {name}")
                result.extend(TaskFormatter.format_structure(content, indent + 1))

        return result

    @staticmethod
    def to_text(structure):
        lines = TaskFormatter.format_structure(structure)
        return "\n".join(lines)
    




# apps/terminal/tasks.py (yoki sizning appingiz yo'li)

from celery import shared_task

@shared_task
def async_check_task(user_id, task_id, workspace_path):
    try:
        task = Task.objects.get(id=task_id, user_id=user_id)
        # Og'ir tekshirish jarayoni orqa fonda ketadi
        is_success = TaskChecker.check(workspace_path, task)
        
        # Diqqat: ProgressManager bazani yangilaydi
        ProgressManager.update(task.user, task, is_success)
        
        return f"Task {task_id} tekshirildi. Natija: {is_success}"
    except Exception as e:
        return f"Xatolik: {str(e)}"

