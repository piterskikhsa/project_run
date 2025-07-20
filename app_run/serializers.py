from random import choice

from django.contrib.auth import get_user_model
from rest_framework import serializers

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem

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
    rating = serializers.SerializerMethodField()

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
            'rating',
        ]

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        runs_finished = getattr(obj, 'runs_finished', None)
        if runs_finished is not None:
            return runs_finished
        return Run.objects.filter(athlete=obj, status=Run.FINISHED).count()

    def get_rating(self, obj):
        return getattr(obj, 'rating', None)

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
            'distance',
            'run_time_seconds',
            'speed',
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
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    class Meta:
        model = Position
        fields = [
            'id',
            'run',
            'latitude',
            'longitude',
            'date_time',
            'distance',
            'speed',
            'created_at',
        ]

    def validate_run(self, value):
        if value.status != Run.IN_PROGRESS:
            raise serializers.ValidationError('Run is not in progress')
        return value


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = [
            'id',
            'name',
            'uid',
            'value',
            'latitude',
            'longitude',
            'picture',
        ]


class UserDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(source='collectible_items', many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['items']


class AthleteUserDetailSerializer(UserDetailSerializer):
    coach = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields + ['coach']

    def get_coach(self, obj):
        coach = obj.coaches.order_by('?').values('coach_id').first()
        if coach is not None:
            return coach.get('coach_id')
        return None


class CoachUserDetailSerializer(UserDetailSerializer):
    athletes = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields + ['athletes']

    def get_athletes(self, obj):
        athletes = obj.athletes.values_list('athlete_id', flat=True)
        return athletes


class AthleteSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class ChallengeSummarySerializer(serializers.Serializer):
    name_to_display = serializers.CharField(read_only=True)
    athletes = AthleteSummarySerializer(many=True, read_only=True)

    class Meta:
        fields = [
            'name_to_display',
            'athletes',
        ]
