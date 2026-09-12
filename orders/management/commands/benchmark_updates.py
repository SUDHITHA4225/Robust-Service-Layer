import time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import F

from orders.models import Order, UserStats


class Command(BaseCommand):
    help = 'Compare N+1 per-order stat updates with a bulk service update.'

    def handle(self, *args, **options):
        user = self._benchmark_user()
        signal_start = time.perf_counter()
        for _ in range(1000):
            order = Order.objects.create(user=user, total=Decimal('1.00'))
            UserStats.objects.get_or_create(user=user)
            UserStats.objects.filter(user=user).update(
                order_count=F('order_count') + 1,
                total_spent=F('total_spent') + order.total,
            )
        signal_time = time.perf_counter() - signal_start

        service_start = time.perf_counter()
        orders = [Order(user=user, total=Decimal('1.00')) for _ in range(1000)]
        Order.objects.bulk_create(orders)
        UserStats.objects.get_or_create(user=user)
        UserStats.objects.filter(user=user).update(
            order_count=F('order_count') + len(orders),
            total_spent=F('total_spent') + Decimal(len(orders)),
        )
        service_time = time.perf_counter() - service_start
        speedup = signal_time / service_time if service_time else 0.0
        self.stdout.write(f'Signal approach time: {signal_time:.6f}s')
        self.stdout.write(f'Optimized service time: {service_time:.6f}s')
        self.stdout.write(f'Speedup factor: {speedup:.2f}x')

    def _benchmark_user(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(username=f'benchmark-{time.time_ns()}')