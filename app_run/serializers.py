from django.contrib.auth import get_user_model
from rest_framework import serializers

from app_run.models import Run, AthleteInfo, Challenge, Position

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
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'date_joined',
            'username',
            'last_name',
            'first_name',
            'type',
            'runs_finished',
        ]

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        runs_finished = getattr(obj, 'runs_finished', None)
        if runs_finished is not None:
            return runs_finished
        return Run.objects.filter(athlete=obj, status=Run.FINISHED).count()

class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserShortSerializer(source='athlete', read_only=True)
    class Meta:
        model = Run
        fields = [
            'id',
            'athlete',
            'created_at',
            'comment',
            'status',
            'athlete_data',
        ]


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    class Meta:
        model = AthleteInfo
        fields = [
            'user_id',
            'goals',
            'weight',
        ]


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'id',
            'full_name',
            'athlete',
        ]


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = [
            'id',
            'run',
            'latitude',
            'longitude',
            'created_at',
        ]

    def validate_run(self, value):
        if value.status != Run.IN_PROGRESS:
            raise serializers.ValidationError('Run is not in progress')
        return value