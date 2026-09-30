from rest_framework import serializers


class TerminalSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class NanoSaveSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=255)
    # 100 KB dan katta fayl saqlanmaydi, bo'sh fayl esa ruxsat etiladi
    content = serializers.CharField(max_length=100_000, allow_blank=True)
