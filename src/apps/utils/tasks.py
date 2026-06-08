# TO'G'RI IMPORT:
from django.db import transaction

from apps.task.models import Task
from apps.task.tasks import  ProgressManager, TaskChecker
from celery.utils.log import get_task_logger

from celery import shared_task

logger = get_task_logger(__name__)
# ==========================================
# CELERY ASINXRON TASK
# ==========================================
@shared_task
def async_check_task(user_id, task_id, workspace_path):
    logger.info(f"User {user_id} uchun Task {task_id} tekshirish boshlandi...")
    
    try:
        # select_related('user') orqali foydalanuvchini bazadan bir urinishda yuklab olamiz (optimizatsiya)
        task = Task.objects.select_related('user__profile').get(id=task_id, user_id=user_id)
        
        # Fayllar strukturasini tekshirish
        is_success = TaskChecker.check(workspace_path, task)
        logger.info(f"Tekshiruv natijasi: {is_success}")
        
        # Bazaga yozish jarayonida xatolik bo'lsa rollback bo'lishi uchun transaction.atomic ishlatamiz
        with transaction.atomic():
            ProgressManager.update(task.user, task, is_success)
        
        return f"Task {task_id} muvaffaqiyatli tekshirildi. Natija: {is_success}"
        
    except Task.DoesNotExist:
        logger.error(f"Task topilmadi: task_id={task_id}, user_id={user_id}")
        return f"Xatolik: Task yoki User topilmadi."
    except Exception as e:
        logger.error(f"Tekshirishda kutilmagan xatolik: {str(e)}")
        return f"Xatolik: {str(e)}"

