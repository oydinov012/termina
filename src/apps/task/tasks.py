import random
from .models import Task, Profile
from apps.task.task_blank import TASK_BANK


class TaskEngine:

    @staticmethod
    def generate(user):

        profile, _ = Profile.objects.get_or_create(user=user)
        level = profile.level

        level_data = TASK_BANK.get(level, TASK_BANK[1])
        tasks = level_data["tasks"]

        task_data = random.choice(tasks)

        return Task.objects.create(
            user=user,
            level=level,
            title=task_data["title"],
            description=task_data["description"],
            target_structure=task_data["structure"],
            xp=task_data.get("xp", 1)
        )
    
import os


class TaskChecker:

    @staticmethod
    def check(workspace, task):

        base = workspace.current_dir
        target = task.target_structure

        return TaskChecker._check_structure(base, target)


    @staticmethod
    def _check_structure(base_path, structure):

        for name, content in structure.items():

            path = os.path.join(base_path, name)

            # CASE 1: FILE
            if content is None:
                if not os.path.isfile(path):
                    return False

            # CASE 2: FOLDER (empty)
            elif isinstance(content, dict) and len(content) == 0:
                if not os.path.isdir(path):
                    return False

            # CASE 3: NESTED FOLDER
            elif isinstance(content, dict):
                if not os.path.isdir(path):
                    return False

                if not TaskChecker._check_structure(path, content):
                    return False

        return True
    


class ProgressManager:

    @staticmethod
    def update(user, task, success):

        profile = user.profile

        if success:

            profile.xp += task.xp
            profile.success_streak += 1

            # level up logic
            if profile.success_streak >= 5:
                profile.level += 1
                profile.success_streak = 0

        else:
            profile.success_streak = 0

        profile.save()

class TaskFormatter:

    @staticmethod
    def format_structure(structure, indent=0):

        result = []

        for name, content in structure.items():

            prefix = "  " * indent

            # file
            if content is None:
                result.append(f"{prefix}📄 {name}")

            # empty folder
            elif isinstance(content, dict) and not content:
                result.append(f"{prefix}📁 {name}")

            # nested folder
            else:
                result.append(f"{prefix}📁 {name}")
                result.extend(
                    TaskFormatter.format_structure(content, indent + 1)
                )

        return result
    



    