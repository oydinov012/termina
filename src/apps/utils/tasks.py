from apps.task.models import Task
from apps.task.tasks import  ProgressManager, TaskChecker


from celery import shared_task

@shared_task
def async_check_task(user_id, task_id, workspace_path):
    try:
        task = Task.objects.get(id=task_id, user_id=user_id)
        is_success = TaskChecker.check(workspace_path, task)
        
        ProgressManager.update(task.user, task, is_success)
        
        return f"Task {task_id} tekshirildi. Natija: {is_success}"
    except Exception as e:
        return f"Xatolik: {str(e)}"

