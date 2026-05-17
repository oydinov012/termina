# views.py

import os

from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import (
    Response
)

from api.serializer.terminal_serializer import (
    TerminalSerializer
)

from apps.utils.funksion import (
    TerminalEngine
)


class TerminalView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = TerminalSerializer(data=request.data)

        serializer.is_valid(
            raise_exception=True
        )

        command = serializer.validated_data[
            "command"
        ]

        workspace = request.user.workspace
        content_to_write = request.data.get("content", "")

        engine = TerminalEngine(
            workspace
        )

        result = engine.execute_command(
            command
        )
        print(result)

        # faqat nano javobini boyitamiz
        if result.get(
            "type"
        ) == "nano":
            print("nano")

            path = result[
                "file_path"
            ]
            print(path)

            abs_path = engine.safe_path(
                path
            )
            print(abs_path)

            try:
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content_to_write)
                
                # Yozilgan kontentni natijaga biriktiramiz
                result["content"] = content_to_write
                result["status"] = "Fayl muvaffaqiyatli saqlandi"
            except Exception as e:
                result["content"] = ""
                result["status"] = f"Xatolik yuz berdi: {str(e)}"

        # 4. Workspace joriy holatini olish
        structure = os.listdir(workspace.current_dir)
        print(result)
        return Response({
            "result": result,
            "current_path": workspace.current_dir.replace(workspace.root_dir, "~"),
            "structure": structure
        })
        