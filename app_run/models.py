from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
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
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='runs')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=INIT)
    distance = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    run_time_seconds = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    speed = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Run'
        verbose_name_plural = 'Runs'

    def __str__(self):
        return f'{self.athlete} - {self.status}'


class AthleteInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='athlete_info', primary_key=True)
    goals = models.TextField(default='',)
    weight = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(899)])

    class Meta:
        verbose_name = 'Athlete Info'
        verbose_name_plural = 'Athlete Info'

    def __str__(self):
        return f'{self.user}'


class Challenge(models.Model):
    full_name = models.CharField(max_length=100)
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return f'{self.athlete} - {self.created_at}'


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='positions')
    latitude = models.DecimalField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)], max_digits=6, decimal_places=4)
    longitude = models.DecimalField(
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        max_digits=7,
        decimal_places=4,
    )
    date_time = models.DateTimeField(null=True)
    distance = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    speed = models.FloatField(validators=[MinValueValidator(0.0)], default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'

    def __str__(self):
        return f'{self.run} - {self.latitude} - {self.longitude}'


class CollectibleItem(models.Model):
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=100, unique=True)
    value = models.IntegerField(default=0)
    latitude = models.DecimalField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)], max_digits=6, decimal_places=4)
    longitude = models.DecimalField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)], max_digits=7, decimal_places=4)
    picture = models.URLField(max_length=250)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='collectible_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Collectible Item'
        verbose_name_plural = 'Collectible Items'

    def __str__(self):
        return f'{self.name} - {self.latitude}:{self.longitude}'


class Subscription(models.Model):
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='athletes')
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coaches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.coach} - {self.athlete}'