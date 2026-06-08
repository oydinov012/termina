from django.http import JsonResponse
from django.views import View
from celery.result import AsyncResult
from apps.task.models import Task

class CeleryTaskStatusView(View):
    def get(self, request, task_id, *args, **kwargs):
        """
        Celery task_id orqali fondagi topshiriq holatini va
        uning natijasini tekshiradigan API.
        """
        result = AsyncResult(task_id)
        
        # Holat: PENDING (Kutmoqda), STARTED (Boshlandi), SUCCESS (Tugadi)
        response_data = {
            "task_id": task_id,
            "status": result.status, # Celery ichki statusi (SUCCESS, PENDING, FAILURE)
        }

        if result.ready(): # Agar Celery ishini tugatgan bo'lsa
            # async_check_task return qilgan matnni oladi
            response_data["result"] = result.result 
            
            # Qo'shimcha: Foydalanuvchining yangilangan oxirgi task holatini ham berib yuboramiz
            # Bu frontendda darhol statusni o'zgartirish (completed/failed) uchun kerak
            if request.user.is_authenticated:
                last_task = Task.objects.filter(user=request.user).last()
                if last_task:
                    response_data["task_status"] = last_task.status # "completed" yoki "failed"
                    response_data["xp"] = request.user.profile.xp
                    response_data["streak"] = request.user.profile.success_streak

        return JsonResponse(response_data)