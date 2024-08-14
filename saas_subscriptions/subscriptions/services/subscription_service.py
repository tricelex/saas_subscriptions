from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from saas_subscriptions.subscriptions.constants import UsageTypeChoices
from saas_subscriptions.subscriptions.models import PlanCost
from saas_subscriptions.subscriptions.models import UsageTracker
from saas_subscriptions.subscriptions.models import UserSubscription


class SubscriptionService:
    def __init__(self, user):
        self.user = user

    def initiate_subscription(self, plan_cost_id, start_date=None):
        """Initiate the subscription process by initializing payment."""
        try:
            plan_cost = PlanCost.objects.get(id=plan_cost_id)
        except PlanCost.DoesNotExist as err:
            raise ValidationError("Invalid PlanCost ID.") from err

        if start_date is None:
            start_date = timezone.now()

        # Initialize payment
        payment_response = self.initialize_payment(
            amount=plan_cost.cost, currency=plan_cost.currency
        )

        if payment_response["status"] == "success":
            # Activate subscription after successful payment
            return self.activate_subscription(plan_cost, start_date)

        # Handle payment failure (optional)
        raise ValidationError("Payment failed. Please try again.")

    def activate_subscription(self, plan_cost, start_date):
        """Activate the subscription after successful payment."""
        with transaction.atomic():
            # Cancel any existing active subscription
            self.cancel_current_subscription()

            # Create a new subscription
            new_subscription = UserSubscription.objects.create(
                user=self.user,
                subscription=plan_cost,
                date_billing_start=start_date,
                date_billing_end=self.calculate_end_date(plan_cost, start_date),
                date_billing_next=self.calculate_next_billing_date(plan_cost, start_date),
                active=True,
                cancelled=False,
                units_remaining=plan_cost.units_included if plan_cost.is_usage_based else None,
            )

            # Assign the user to the appropriate group
            self.assign_group(plan_cost.plan.group)

            # Initialize usage tracker if required
            self.initialize_usage_tracker(new_subscription)

            return new_subscription

    def renew_subscription(self, subscription_id):
        """Renew the subscription."""
        try:
            subscription = UserSubscription.objects.get(id=subscription_id, user=self.user)
        except UserSubscription.DoesNotExist:
            raise ValidationError("Subscription not found.")

        if not subscription.is_active:
            raise ValidationError("Cannot renew an inactive subscription.")

        with transaction.atomic():
            subscription.date_billing_start = timezone.now()
            subscription.date_billing_end = self.calculate_end_date(
                subscription.subscription, subscription.date_billing_start
            )
            subscription.date_billing_next = self.calculate_next_billing_date(
                subscription.subscription, subscription.date_billing_start
            )
            subscription.reset_units()
            subscription.save()

            return subscription

    def cancel_subscription(self, subscription_id):
        """Cancel the subscription."""
        try:
            subscription = UserSubscription.objects.get(id=subscription_id, user=self.user)
        except UserSubscription.DoesNotExist:
            raise ObjectDoesNotExist("Subscription not found.")

        with transaction.atomic():
            subscription.active = False
            subscription.cancelled = True
            subscription.save()

            # Remove the user from the associated group
            self.remove_group(subscription.subscription.plan.group)

            return subscription

    def switch_plan(self, new_plan_cost_id):
        """Switch the user to a new plan."""
        return self.initiate_subscription(new_plan_cost_id)

    def cancel_current_subscription(self):
        """Cancel the current active subscription if it exists."""
        active_subscription = UserSubscription.objects.filter(user=self.user, active=True).first()
        if active_subscription:
            self.cancel_subscription(active_subscription.id)

    def assign_group(self, group):
        """Assign the user to the specified group."""
        if group:
            self.user.groups.clear()
            self.user.groups.add(group)

    def remove_group(self, group):
        """Remove the user from the specified group."""
        if group and group in self.user.groups.all():
            self.user.groups.remove(group)

    def initialize_usage_tracker(self, subscription):
        """Initialize usage tracker for the subscription if it has usage limits."""
        if subscription.subscription.is_usage_based:
            for usage_type in [
                UsageTypeChoices.API_REQUEST,
                UsageTypeChoices.REPORT_GENERATION,
            ]:
                UsageTracker.objects.create(
                    user=self.user, subscription=subscription, usage_type=usage_type
                )

    def calculate_end_date(self, plan_cost, start_date):
        """Calculate the end date based on the plan's recurrence."""
        recurring_units = {
            "0": None,  # ONCE
            "1": timedelta(seconds=1),  # SECOND
            "2": timedelta(minutes=1),  # MINUTE
            "3": timedelta(hours=1),  # HOUR
            "4": timedelta(days=1),  # DAY
            "5": timedelta(weeks=1),  # WEEK
            "6": timedelta(days=30),  # MONTH (Approximation)
            "7": timedelta(days=365),  # YEAR (Approximation)
        }
        return start_date + recurring_units.get(plan_cost.recurrence_unit, None)

    def calculate_next_billing_date(self, plan_cost, start_date):
        """Calculate the next billing date based on the plan's recurrence."""
        return self.calculate_end_date(plan_cost, start_date)

    def initialize_payment(self, amount, currency):
        """Initialize a payment (generic placeholder)."""
        # Placeholder for payment initialization logic
        # This method should interact with your payment service class to handle payments
        return {
            "status": "success",  # Example response; implement actual payment logic
            "transaction_id": "12345",
        }
