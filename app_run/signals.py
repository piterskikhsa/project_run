from django.db.models.signals import post_save
from django.dispatch import receiver

from app_run.helpers import get_distance
from app_run.models import Position, CollectibleItem

DISTANCE_RAD = 100

@receiver(post_save, sender=Position)
def collect_items(sender, instance, created, **kwargs):
    if not created:
        return
    items = CollectibleItem.objects.annotate(
      distance=get_distance(instance.latitude, instance.longitude)
    ).filter(
        distance__lte=DISTANCE_RAD
    )
    user = instance.run.athlete
    user.collectible_items.add(*items)

