from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_run.views import (
    company_details,
    RunViewSet,
    UserViewSet,
    AthleteInfoApiView,
    ChallengeViewSet,
    PositionViewSet,
    CollectibleItemViewSet,
    UploadCollectibleItemFileView,
)

router = DefaultRouter()
router.register('runs', RunViewSet, basename='runs')
router.register('users', UserViewSet, basename='users')
router.register('challenges', ChallengeViewSet, basename='challenges')
router.register('positions', PositionViewSet, basename='positions')
router.register('collectible_item', CollectibleItemViewSet, basename='collectible_items')

urlpatterns = [
    path('company_details/', company_details, name='company_details'),
    path('athlete_info/<int:user_id>/', AthleteInfoApiView.as_view(), name='athlete_info'),
    path('upload_file/', UploadCollectibleItemFileView.as_view(), name='upload_file'),
    path('', include(router.urls)),
]
