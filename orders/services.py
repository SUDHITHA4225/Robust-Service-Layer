from django.db import transaction
from django.db.models import F

from .models import Order, UserStats


@transaction.atomic
def create_order(user, total):
    order = Order.objects.create(user=user, total=total)
    UserStats.objects.get_or_create(user=user)
    UserStats.objects.filter(user=user).update(
        order_count=F('order_count') + 1,
        total_spent=F('total_spent') + total,
    )
    stats = UserStats.objects.get(user=user)
    return order, stats