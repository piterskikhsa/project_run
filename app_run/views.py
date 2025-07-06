from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer

User = get_user_model()


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
        run.save()
        return Response(RunSerializer(run).data, status=200)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.exclude(is_superuser=True).annotate(runs_finished=Count('runs', filter=Q(runs__status=Run.FINISHED)))
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']
    pagination_class = PagePagination

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
