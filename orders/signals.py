from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, UserStats


@receiver(post_save, sender=Order)
def update_user_stats_on_order_created(sender, instance, created, **kwargs):
    if not created:
        return
    stats, _ = UserStats.objects.get_or_create(user=instance.user)
    stats.order_count += 1
    stats.total_spent += instance.total
    stats.save(update_fields=['order_count', 'total_spent'])