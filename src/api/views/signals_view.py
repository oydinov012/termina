from django.http import JsonResponse
from django.views import View
from celery.result import AsyncResult
from apps.task.models import Task



class CeleryTaskStatusView(View):
    def get(self, request, task_id, *args, **kwargs):
        result = AsyncResult(task_id)
        
        response_data = {
            "task_id": task_id,
            "status": result.status, 
        }

        if result.ready():
            response_data["result"] = str(result.result)
            
            # 🔥 Agar request.user bo'sh bo'lsa, joriy sessiyadagi oxirgi task orqali foydalanuvchini topamiz
            user = request.user if request.user.is_authenticated else None
            
            # Agar requestda aniqlanmasa, Celery yangilagan oxirgi task egasini qidiramiz
            last_task = None
            if user:
                last_task = Task.objects.filter(user=user).last()
            else:
                # Task modelidan oxirgi in_progress bo'lmagan topshiriq egasini olish
                last_task = Task.objects.filter(status__in=["completed", "failed"]).last()
                if last_task:
                    user = last_task.user

            if last_task and user:
                response_data["task_status"] = last_task.status
                response_data["xp"] = user.profile.xp
                response_data["streak"] = user.profile.success_streak

        return JsonResponse(response_data)