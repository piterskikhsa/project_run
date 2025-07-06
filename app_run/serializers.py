from django.contrib.auth import get_user_model
from rest_framework import serializers

from app_run.models import Run


User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'last_name',
            'first_name',
        ]


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'date_joined',
            'username',
            'last_name',
            'first_name',
            'type',
        ]

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserShortSerializer(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = [
            'athlete',
            'created_at',
            'comment',
            'id',
            'athlete_data',
        ]
