from django.contrib import admin

from saas_subscriptions.subscriptions.models import PlanCost
from saas_subscriptions.subscriptions.models import SubscriptionPlan
from saas_subscriptions.subscriptions.models import UsageTracker
from saas_subscriptions.subscriptions.models import UserSubscription

# Register your models here.
admin.site.register(UserSubscription)
admin.site.register(PlanCost)
admin.site.register(UsageTracker)
admin.site.register(SubscriptionPlan)
