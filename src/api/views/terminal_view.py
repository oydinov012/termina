# views.py

import os

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.terminal.models import Workspace
from api.serializer.terminal_serializer import (
    TerminalSerializer,
    NanoSaveSerializer
)

from apps.utils.funksion import TerminalEngine


# ===================================================
# TERMINAL
# ===================================================

class TerminalView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = TerminalSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        command = serializer.validated_data[
            "command"
        ]

        workspace = request.user.workspace

        engine = TerminalEngine(workspace)

        result = engine.execute_command(command)

        structure = os.listdir(
            workspace.current_dir
        )

        return Response({

            "result": result,

            "current_path":
                workspace.current_dir.replace(
                    workspace.root_dir,
                    "~"
                ),

            "structure": structure
        })


# ===================================================
# NANO OPEN
# ===================================================

class NanoView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        path = request.GET.get("path")

        workspace = request.user.workspace

        abs_path = os.path.abspath(
            os.path.join(
                workspace.current_dir,
                path
            )
        )

        if not abs_path.startswith(
            workspace.root_dir
        ):

            return Response({
                "error": "Ruxsat yo'q"
            }, status=403)

        if not os.path.exists(abs_path):

            open(abs_path, "w").close()

        with open(
            abs_path,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        return Response({

            "path": path,

            "content": content
        })


# ===================================================
# NANO SAVE
# ===================================================

class NanoSaveView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = NanoSaveSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        path = serializer.validated_data["path"]

        content = serializer.validated_data[
            "content"
        ]
        print('path', path)
        print('content', content)

        workspace = request.user.workspace

        abs_path = os.path.abspath(
            os.path.join(
                workspace.current_dir,
                path
            )
        )

        if not abs_path.startswith(
            workspace.root_dir
        ):

            return Response({
                "error": "Ruxsat yo'q"
            }, status=403)

        with open(
            abs_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        return Response({

            "message": "Saqlandi",

            "return_path":
                workspace.current_dir.replace(
                    workspace.root_dir,
                    "~"
                )
        })