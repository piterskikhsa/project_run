from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from app_run.models import Position, CollectibleItem

DISTANCE_RAD = 100 * 0.1988


@receiver(post_save, sender=Position)
def collect_items(sender, instance, **kwargs):

    latitude_range = [Decimal(float(instance.latitude) - 100 * 0.1988) , Decimal(float(instance.latitude) + DISTANCE_RAD / 2)]
    longitude_range = [Decimal(float(instance.longitude) - 100 * 0.1988), Decimal(float(instance.longitude) + DISTANCE_RAD / 2)]
    items = CollectibleItem.objects.filter(
        latitude__range=latitude_range,
        longitude__range=longitude_range,
    )
    user = instance.run.athlete
    user.collectible_items.add(*items)

