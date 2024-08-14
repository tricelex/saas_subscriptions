from rest_framework import serializers

from saas_subscriptions.subscriptions.models import PlanCost
from saas_subscriptions.subscriptions.models import SubscriptionPlan
from saas_subscriptions.subscriptions.models import UserSubscription


class PlanCostSerializer(serializers.ModelSerializer):
    """PlanCost model serializer with property fields  exposed as serializer method fields"""

    class Meta:
        model = PlanCost
        fields = "__all__"


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model and Tags can be created directly on it"""

    costs = PlanCostSerializer(many=True, read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = "__all__"


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """User subscription model serializer"""

    class Meta:
        model = UserSubscription
        fields = "__all__"
