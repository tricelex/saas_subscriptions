from rest_framework import routers

from saas_subscriptions.subscriptions.api.api_views import PlanCostViewSet
from saas_subscriptions.subscriptions.api.api_views import SubscriptionPlanViewSet
from saas_subscriptions.subscriptions.api.api_views import UserSubscriptionViewSet

app_name = "subscriptions_api"

router = routers.SimpleRouter()
router.register("plan-costs", PlanCostViewSet, basename="plan-costs")
router.register("subscription-plans", SubscriptionPlanViewSet, basename="subscription-plans")
router.register("user-subscriptions", UserSubscriptionViewSet, basename="user-subscriptions")

urlpatterns = router.urls
