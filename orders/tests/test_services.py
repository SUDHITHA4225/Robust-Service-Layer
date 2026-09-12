from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test import TestCase

from orders import services
from orders.models import Order, UserStats
from orders.signals import update_user_stats_on_order_created


class OrderServiceTests(TestCase):
    def setUp(self):
        post_save.disconnect(receiver=update_user_stats_on_order_created, sender=Order)

    def tearDown(self):
        post_save.disconnect(receiver=update_user_stats_on_order_created, sender=Order)

    def test_create_order_updates_user_stats(self):
        user = get_user_model().objects.create_user(username='service-user')
        order, stats = services.create_order(user, Decimal('19.95'))
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())
        stats.refresh_from_db()
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(stats.total_spent, Decimal('19.95'))
        self.assertEqual(UserStats.objects.get(user=user).pk, stats.pk)

    def test_plain_model_creation_does_not_update_stats(self):
        user = get_user_model().objects.create_user(username='plain-user')
        Order.objects.create(user=user, total=Decimal('3.00'))
        self.assertFalse(UserStats.objects.filter(user=user).exists())