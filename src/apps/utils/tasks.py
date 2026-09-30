from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from apps.task.models import Task
from apps.task.tasks import ProgressManager, TaskChecker

logger = get_task_logger(__name__)


@shared_task
def async_check_task(user_id, task_id, workspace_path):
    """Topshiriqni fonda tekshiradi.

    select_for_update() qatorni qulflaydi: bir xil task uchun ketma-ket yuborilgan
    bir nechta vazifa navbat bilan ishlaydi va bajarilgan taskka XP ikki marta
    qo'shilmaydi.
    """
    logger.info("User %s uchun Task %s tekshirish boshlandi", user_id, task_id)

    try:
        with transaction.atomic():
            task = Task.objects.select_for_update().get(id=task_id, user_id=user_id)

            if task.status == "completed":
                return f"Task {task_id} allaqachon bajarilgan."

            is_success = TaskChecker.check(workspace_path, task)
            ProgressManager.update(task.user, task, is_success)

        logger.info("Tekshiruv natijasi: %s", is_success)
        return f"Task {task_id} tekshirildi. Natija: {is_success}"

    except Task.DoesNotExist:
        logger.error("Task topilmadi: task_id=%s user_id=%s", task_id, user_id)
        return "Xatolik: Task topilmadi."
