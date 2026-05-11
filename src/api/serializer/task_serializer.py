from rest_framework import serializers


class TaskCheckSerializer(serializers.Serializer):

    task_id = serializers.IntegerField()