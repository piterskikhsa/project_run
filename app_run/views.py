from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app_run.models import Run
from app_run.serializers import RunSerializer


@api_view(['GET'])
def company_details(request):
    company_info = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.COMPANY_SLOGAN,
        'contacts': settings.COMPANY_CONTACTS,
    }
    return Response(company_info)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
