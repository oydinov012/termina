from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.task.models import Task
from api.serializer.task_serializer import TaskCheckSerializer
import os
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from apps.task.tasks import TaskChecker, TaskEngine, ProgressManager, TaskFormatter



class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Foydalanuvchiga topshiriqni yuklash",
        responses={
            200: inline_serializer(
                name='TaskRetrieveResponse',
                fields={
                    'task_id': serializers.IntegerField(),
                    'title': serializers.CharField(),
                    'description': serializers.CharField(),
                    'level': serializers.IntegerField(),
                    'xp': serializers.IntegerField(),
                    'status': serializers.CharField(),
                    'structure': serializers.DictField(), 
                    'formatted_structure': serializers.CharField(),
                }
            )
        },
        tags=['task']
    )
    def get(self, request):

        task = TaskEngine.generate(
            request.user
        )

        return Response({

            "task_id": task.id,

            "title": task.title,

            "description": task.description,

            "level": task.level,

            "xp": task.xp,

            "status": task.status,

            "structure": task.target_structure,

            "formatted_structure":
                TaskFormatter.to_text(
                    task.target_structure
                ),

            "template": {
                "id": task.template.id,
                "type": task.template.type,
                "difficulty":
                    task.template.difficulty,
                "command":
                    task.template.command,
            },

            "categories": [

                {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                }

                for category in
                task.template.categories.all()
            ]
        })
    @extend_schema(
        summary="Yaratilgan fayllar strukturasini tekshirish",
        request=TaskCheckSerializer,
        responses={
            200: inline_serializer(
                name='TaskCheckResponse',
                fields={
                    'status': serializers.CharField(),
                    'message': serializers.CharField(),
                }
            )
        },
        tags=['task']
    )
    def post(self, request):
        serializer = TaskCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Boshqa foydalanuvchining taski yoki mavjud bo'lmagan ID uchun 404 qaytadi
        task = get_object_or_404(
            Task,
            id=serializer.validated_data["task_id"],
            user=request.user,
        )

        if task.status == "completed":
            return Response(
                {"status": "already_completed", "message": "Bu topshiriq allaqachon bajarilgan."}
            )

        # Terminaldagi `start` buyrug'i yaratgan papka bilan bir xil yo'l
        workspace = request.user.workspace
        task_dir = os.path.join(workspace.root_dir, f"task_{task.id}_papkasi")

        if not os.path.isdir(task_dir):
            return Response(
                {
                    "status": "error",
                    "message": "Avval terminalda `start <task_id>` buyrug'ini bajaring.",
                },
                status=400,
            )

        success = TaskChecker.check(task_dir, task)
        ProgressManager.update(request.user, task, success)

        profile = request.user.profile
        if success:
            return Response({
                "status": "correct",
                "xp": profile.xp,
                "level": profile.level,
            })

        return Response({
            "status": "wrong",
            "hint": "Qayta urinib ko'ring",
        })