# serializers.py

from rest_framework import serializers


class TerminalSerializer(serializers.Serializer):

    command = serializers.CharField()


class NanoSaveSerializer(serializers.Serializer):

    path = serializers.CharField()

    content = serializers.CharField()