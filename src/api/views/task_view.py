from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.task.models import Task
from api.serializer.task_serializer import TaskCheckSerializer
from apps.task.tasks import TaskChecker, TaskEngine, ProgressManager, TaskFormatter


class TaskView(APIView):

    permission_classes = [IsAuthenticated]

    # GET TASK
    def get(self, request):

        task = TaskEngine.generate(request.user)

        
        return Response({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "xp": task.xp,
            "level": task.level,
            "structure": TaskFormatter.format_structure(task.target_structure)
        })
    
    # CHECK TASK
    def post(self, request):

        serializer = TaskCheckSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        task = Task.objects.get(
            id=serializer.validated_data["task_id"],
            user=request.user
        )
        print(task)
        print(serializer)

        workspace = request.user.workspace

        result = TaskChecker.check(workspace, task)
        print(result)
        ProgressManager.update(request.user, task, result)

        if result:

            task.is_completed = True
            task.save()

            return Response({
                "status": "correct ✔",
                "xp": request.user.profile.xp,
                "level": request.user.profile.level
            })

        return Response({
            "status": "wrong ❌",
            "hint": "Try again"
        })