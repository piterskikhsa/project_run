from rest_framework import serializers

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ['athlete', 'created_at', 'comment']