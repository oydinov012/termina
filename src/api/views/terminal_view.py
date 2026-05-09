from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.terminal.models import Workspace
from api.serializer.terminal_serializer import TerminalSerializer
from apps.utils.funksion import execute_command
import os

class TerminalView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request)
        serializer = TerminalSerializer(data=request.data)
        if serializer.is_valid():
            command = serializer.validated_data.get('command', '')
            
            # Foydalanuvchi workspace'ini olish
            try:
                workspace = request.user.workspace
            except Workspace.DoesNotExist:
                return Response({"error": "Workspace topilmadi"}, status=404)
            
            # Buyruqni bajarish
            output = execute_command(workspace, command)
            
            # Yon oyna (file tree) uchun fayllarni olish
            # Bu yerda biz joriy papkadagi barcha fayllarni qaytaramiz
            files_list = os.listdir(workspace.current_dir)
            
            return Response({
                "output": output,
                "current_path": workspace.current_dir.replace(workspace.root_dir, "~"),
                "structure": files_list
            })
        return Response(serializer.errors, status=400)