from django.conf import settings
from django.db import models


class Run(models.Model):
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Run'
        verbose_name_plural = 'Runs'

    def __str__(self):
        return f'{self.athlete} - {self.created_at}'