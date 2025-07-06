from django.urls import path

from app_run.views import company_details

urlpatterns = [
    path("company_details/", company_details, name="company_details"),
]
