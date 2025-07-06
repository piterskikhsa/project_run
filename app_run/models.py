from django.conf import settings
from django.db import models


class Run(models.Model):
    INIT = 'init'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'
    STATUS_CHOICES = [
        (INIT, 'Created'),
        (IN_PROGRESS, 'Started'),
        (FINISHED, 'Finished'),
    ]
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=INIT)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Run'
        verbose_name_plural = 'Runs'

    def __str__(self):
        return f'{self.athlete} - {self.created_at}'