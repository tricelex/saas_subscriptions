from rest_framework import viewsets

from saas_subscriptions.subscriptions.api import serializers
from saas_subscriptions.subscriptions.models import PlanCost
from saas_subscriptions.subscriptions.models import SubscriptionPlan
from saas_subscriptions.subscriptions.models import UserSubscription


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = serializers.SubscriptionPlanSerializer


class PlanCostViewSet(viewsets.ModelViewSet):
    queryset = PlanCost.objects.all()
    serializer_class = serializers.PlanCostSerializer


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSubscriptionSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserSubscription.objects.all()
        return UserSubscription.objects.filter(user=self.request.user)
