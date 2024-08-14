import factory
from faker import Faker

from saas_subscriptions.subscriptions.models import SubscriptionPlan

fake = Faker()


class SubscriptionPlanFactory(factory.django.DjangoModelFactory):
    """SubscriptionPlan factory class."""

    class Meta:
        model = SubscriptionPlan
