from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.task.models import Task
from api.serializer.task_serializer import TaskCheckSerializer
from apps.task.tasks import TaskChecker, TaskEngine, ProgressManager, TaskFormatter



class TaskView(APIView):

    permission_classes = [IsAuthenticated, ]
    
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
                "status": "correct ✔ ",
                "xp": request.user.profile.xp,
                "level": request.user.profile.level
            })

        return Response({
            "status": "wrong ❌",
            "hint": "Try again"
        })