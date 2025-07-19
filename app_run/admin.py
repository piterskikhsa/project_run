from django.contrib import admin

from app_run.models import Run, CollectibleItem


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'created_at', 'comment')
    list_filter = ('created_at',)


@admin.register(CollectibleItem)
class CollectibleItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'value', 'latitude', 'longitude', 'picture', 'created_at')
    list_filter = ('created_at',)