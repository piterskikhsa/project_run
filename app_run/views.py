
import openpyxl
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Max, Min, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from geopy.distance import geodesic

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import (
    RunSerializer,
    UserSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
    PositionSerializer,
    CollectibleItemSerializer,
    UserDetailSerializer,
)

User = get_user_model()

def calculate_distance(positions):
    way = [(position.latitude, position.longitude) for position in positions]
    return geodesic(*way).kilometers


def calculate_speed(start_time, end_time, distance_meters):
    time = (end_time - start_time).total_seconds()
    if time != 0:
        return round(distance_meters / time, 2)
    return 0


class PagePagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 100


@api_view(['GET'])
def company_details(request):
    company_info = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.COMPANY_SLOGAN,
        'contacts': settings.COMPANY_CONTACTS,
    }
    return Response(company_info)


def calculate_time(run_id):
    try:
        times = Position.objects.filter(run=run_id).aggregate(
            start_time=Min('date_time'),
            end_time=Max('date_time'),
        )
        return (times['end_time'] - times['start_time']).total_seconds()
    except TypeError as e:
        print(e)
        return 0


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']
    pagination_class = PagePagination


    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        run = self.get_object()
        if run.status != Run.INIT:
            return Response({'message': 'Run already started'}, status=400)
        run.status = Run.IN_PROGRESS
        run.save()
        return Response(RunSerializer(run).data, status=200)

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        run = self.get_object()
        if run.status != Run.IN_PROGRESS:
            return Response({'message': 'Run already finished or not started'}, status=400)
        run.status = Run.FINISHED
        run.run_time_seconds = calculate_time(run_id=run.id)
        run.distance = calculate_distance(run.positions.all())
        run.speed = run.positions.aggregate(speed=Avg('speed'))['speed']
        run.save()
        self.create_challenge(run)
        return Response(RunSerializer(run).data, status=200)

    def create_challenge(self, run):
        runs_finished = Run.objects.filter(athlete=run.athlete, status=Run.FINISHED).aggregate(
            distance_sum=Sum('distance'), count=Count('id')
        )
        if runs_finished.get('count', 0) == 10:
            Challenge.objects.create(athlete=run.athlete, full_name='Сделай 10 Забегов!')
        if runs_finished.get('distance_sum', 0.0) >= 50.0:
            Challenge.objects.get_or_create(athlete=run.athlete, full_name='Пробеги 50 километров!')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).annotate(runs_finished=Count('runs', filter=Q(runs__status=Run.FINISHED)))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = PagePagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = self.queryset
        user_type = self.request.query_params.get('type', None)
        if user_type == 'coach':
            qs = qs.filter(is_staff=True)
        elif user_type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class AthleteInfoApiView(APIView):
    def get(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(user=user)
        return Response(AthleteInfoSerializer(athlete_info).data)

    def put(self, request, user_id=None):
        data = request.data
        user = get_object_or_404(User, pk=user_id)
        athlete_info, _ = AthleteInfo.objects.get_or_create(user=user)
        serializer = AthleteInfoSerializer(instance=athlete_info, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ['athlete',]
    pagination_class = PagePagination


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_fields = ['run',]
    pagination_class = PagePagination

    def perform_create(self, serializer):
        distance = 0
        speed = 0
        run = serializer.validated_data['run']
        last_position = Position.objects.filter(run=run).order_by('date_time').last()
        if last_position:
            d = geodesic((last_position.latitude, last_position.longitude), (serializer.validated_data['latitude'], serializer.validated_data['longitude'])).meters
            distance = round(last_position.distance + d, 2)
            speed = calculate_speed(start_time=last_position.date_time, end_time=serializer.validated_data['date_time'], distance_meters=d)

        serializer.validated_data['distance'] = distance
        serializer.validated_data['speed'] = speed
        serializer.save()


class CollectibleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer
    pagination_class = PagePagination


def process_file(file):
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active
    collectible_items = []
    row_errors = []
    column_names = ['name', 'uid', 'value', 'latitude', 'longitude', 'picture']
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if all(value is None for value in row):
            continue

        item_row = {name: value for name, value in zip(column_names, row)}
        item = CollectibleItem(**item_row)
        serializer = CollectibleItemSerializer(data=item_row)
        if serializer.is_valid():
            collectible_items.append(item)
        else:
            row_errors.append(row)

    CollectibleItem.objects.bulk_create(
        collectible_items,
        batch_size=1000,
        update_conflicts=True,
        update_fields=['name', 'value', 'latitude', 'longitude', 'picture'],
        unique_fields=['uid']
    )
    return row_errors


class UploadCollectibleItemFileView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        errors = process_file(file)
        return Response(data=errors, status=status.HTTP_200_OK)
