from rest_framework import serializers

class TerminalSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=255, allow_blank=True)