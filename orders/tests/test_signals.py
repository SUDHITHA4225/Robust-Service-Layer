from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test import TestCase

from orders.models import Order, UserStats
from orders.signals import update_user_stats_on_order_created


class SignalBehaviorTests(TestCase):
    def setUp(self):
        post_save.connect(update_user_stats_on_order_created, sender=Order)

    def tearDown(self):
        post_save.disconnect(receiver=update_user_stats_on_order_created, sender=Order)

    def test_order_creation_updates_stats(self):
        user = get_user_model().objects.create_user(username='signal-user')
        Order.objects.create(user=user, total=Decimal('12.50'))
        stats = UserStats.objects.get(user=user)
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(stats.total_spent, Decimal('12.50'))

    def test_bulk_update_bypasses_signal(self):
        first = get_user_model().objects.create_user(username='first-user')
        other = get_user_model().objects.create_user(username='other-user')
        Order.objects.create(user=first, total=Decimal('10.00'))
        Order.objects.create(user=first, total=Decimal('20.00'))
        initial = UserStats.objects.get(user=first)
        self.assertEqual(initial.order_count, 2)
        Order.objects.create(user=first, total=Decimal('5.00'))
        self.assertEqual(UserStats.objects.get(user=first).order_count, 3)
        bulk_orders = [Order(user=other, total=Decimal('7.00')) for _ in range(3)]
        Order.objects.bulk_create(bulk_orders)
        Order.objects.filter(user=other).update(user=first)
        stats = UserStats.objects.get(user=first)
        self.assertEqual(stats.order_count, 3)
        self.assertEqual(stats.total_spent, Decimal('35.00'))