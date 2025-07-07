from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import (
    company_details,
    RunViewSet,
    UserViewSet,
    AthleteInfoApiView,
    ChallengeViewSet,
)

router = DefaultRouter()
router.register('runs', RunViewSet, basename='runs')
router.register('users', UserViewSet, basename='users')
router.register('challenges', ChallengeViewSet, basename='challenges')

urlpatterns = [
    path('company_details/', company_details, name='company_details'),
    path('athlete_info/<int:user_id>/', AthleteInfoApiView.as_view(), name='athlete_info'),
    path('', include(router.urls)),
]
