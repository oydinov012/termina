

from celery.result import AsyncResult
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.task.models import Task


class CeleryTaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        # Faqat shu foydalanuvchining topshirig'i. Boshqasining ID si bo'lsa, 404 qaytadi.
        task = get_object_or_404(
            Task, check_job_id=task_id, user=request.user
        )

        result = AsyncResult(task_id)
        data = {
            "task_id": task_id,
            "status": result.status,
        }

        if result.ready():
            profile = request.user.profile
            data.update({
                "task_status": task.status,
                "xp": profile.xp,
                "level": profile.level,
                "streak": profile.success_streak,
            })

        return Response(data)