import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

# drf-spectacular vositalari
from drf_spectacular.utils import extend_schema, inline_serializer, PolymorphicProxySerializer

# Serializer va Engine importlari (o'zingizning loyha tuzilmangizga moslang)
from api.serializer.terminal_serializer import TerminalSerializer, NanoSaveSerializer
from apps.utils.funksion import TerminalEngine

class TerminalView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PolymorphicProxySerializer(
            component_name='TerminalInput',
            serializers={
                'regular_command': TerminalSerializer,
                'nano_save': NanoSaveSerializer,
            },
            resource_type_field_name='type',  # YAML'dagi discriminator.propertyName
        ),
        responses={
            200: inline_serializer(
                name='TerminalResponse',
                fields={
                    'result': inline_serializer(
                        name='TerminalResultDetail',
                        fields={
                            'type': serializers.CharField(required=False, allow_null=True),
                            'file_path': serializers.CharField(required=False, allow_null=True),
                            'content': serializers.CharField(required=False, allow_null=True),
                            'status': serializers.CharField(required=False, allow_null=True),
                            'output': serializers.CharField(required=False, allow_null=True),
                        }
                    ),
                    'current_path': serializers.CharField(),
                    'structure': serializers.ListField(child=serializers.CharField())
                }
            )
        },
        tags=['terminal']
    )
    def post(self, request):
        workspace = request.user.workspace
        engine = TerminalEngine(workspace)
        result = {}

        # YAML schemaga muvofiq discriminator 'type' maydonini olamiz
        request_type = request.data.get("type", None)

        # 1-HOLAT: Oddiy buyruq (ls, cd, mkdir) yoki nano yordamida faylni ochish
        if request_type == "regular_command" or "command" in request.data:
            serializer = TerminalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            command = serializer.validated_data["command"]
            
            # Terminal engineda buyruqni bajaramiz
            result = engine.execute_command(command)
            
            # Agar bajarilgan buyruq nano bo'lsa, faylni o'qib kontentini qaytaramiz
            if result.get("type") == "nano":
                path = result.get("file_path", "")
                abs_path = engine.safe_path(path)
                
                current_content = ""
                if os.path.isfile(abs_path):
                    try:
                        with open(abs_path, "r", encoding="utf-8") as f:
                            current_content = f.read()
                    except Exception:
                        current_content = "Faylni o'qib bo'lmadi."
                
                result["content"] = current_content
                result["status"] = "Fayl muvaffaqiyatli ochildi"

        # 2-HOLAT: Nano muharriri ichida faylni saqlash (Ctrl+O bosilganda)
        elif request_type == "nano_save" or ("path" in request.data and "content" in request.data):
            serializer = NanoSaveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            path = serializer.validated_data["path"]
            content_to_write = serializer.validated_data["content"]
            abs_path = engine.safe_path(path)
            
            try:
                # Faylga yozish jarayoni
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(content_to_write)
                
                result = {
                    "type": "nano",
                    "file_path": path,
                    "content": content_to_write,
                    "status": "Fayl muvaffaqiyatli saqlandi",
                    "output": ""
                }
            except Exception as e:
                result = {
                    "type": "nano",
                    "file_path": path,
                    "content": "",
                    "status": f"Xatolik yuz berdi: {str(e)}",
                    "output": ""
                }
        else:
            return Response(
                {"detail": "Noto'g'ri so'rov formati. 'type' kaliti ('regular_command' yoki 'nano_save') berilishi shart."}, 
                status=400
            )

        # Skrinshotdagi o'ng tomondagi "Siz yaratgan joriy fayllar strukturasi" uchun:
        try:
            structure = os.listdir(workspace.current_dir)
        except Exception:
            structure = []
        
        return Response({
            "result": result,
            "current_path": workspace.current_dir.replace(workspace.root_dir, "~"),
            "structure": structure
        })