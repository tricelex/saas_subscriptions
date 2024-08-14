from django.test import TestCase

from tests.subscriptions.factories import SubscriptionPlanFactory


class SubscriptionPlanTests(TestCase):
    def setUp(self):
        self.sub_plan = SubscriptionPlanFactory()

    def test_str(self):
        """Test string representation of service."""
        self.assertEqual(str(self.sub_plan), "")
