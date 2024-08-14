from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models

from saas_subscriptions.subscriptions.constants import BillingTypeChoices
from saas_subscriptions.subscriptions.constants import CurrencyChoices
from saas_subscriptions.subscriptions.constants import UsageTypeChoices

ONCE = "0"
SECOND = "1"
MINUTE = "2"
HOUR = "3"
DAY = "4"
WEEK = "5"
MONTH = "6"
YEAR = "7"
RECURRENCE_UNIT_CHOICES = (
    (ONCE, "once"),
    (SECOND, "second"),
    (MINUTE, "minute"),
    (HOUR, "hour"),
    (DAY, "day"),
    (WEEK, "week"),
    (MONTH, "month"),
    (YEAR, "year"),
)


class SubscriptionPlan(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    plan_name = models.CharField(max_length=128, db_index=True)
    plan_description = models.CharField(max_length=512, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, related_name="plans", blank=True, null=True
    )
    grace_period = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("plan_name",)

    def __str__(self):
        return self.plan_name


class PlanCost(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    plan = models.ForeignKey(
        "SubscriptionPlan",
        on_delete=models.CASCADE,
        related_name="costs",
        db_index=True,
    )
    slug = models.SlugField(blank=True, max_length=128, null=True, unique=True)
    recurrence_period = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)], blank=True, null=True
    )
    recurrence_unit = models.CharField(
        choices=RECURRENCE_UNIT_CHOICES, default=MONTH, max_length=1, blank=True
    )
    cost = models.DecimalField(decimal_places=4, max_digits=19, blank=True, null=True)
    billing_type = models.IntegerField(choices=BillingTypeChoices.choices)
    units_included = models.PositiveIntegerField(default=0, blank=True, null=True)
    api_limit = models.PositiveIntegerField(default=0, help_text="API requests limit")
    report_limit = models.PositiveIntegerField(default=0, help_text="Report generation limit")
    currency = models.IntegerField(choices=CurrencyChoices.choices, default=CurrencyChoices.NGN)

    class Meta:
        ordering = (
            "recurrence_unit",
            "recurrence_period",
            "cost",
        )

    def __str__(self):
        return f"{self.plan.plan_name} - {self.cost} - {self.currency}"

    @property
    def is_usage_based(self):
        return self.billing_type == BillingTypeChoices.USAGE_BASED

    @property
    def is_time_based(self):
        return self.billing_type == BillingTypeChoices.TIME_BASED

    @property
    def currency_denomination(self):
        """Returns the full denomination of the currency."""
        denomination_map = {
            CurrencyChoices.USD: "United States Dollar",
            CurrencyChoices.EUR: "Euro",
            CurrencyChoices.GBP: "British Pound",
            CurrencyChoices.NGN: "Nigerian Naira",
        }
        return denomination_map.get(self.currency, "Unknown Currency")


class UserSubscription(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="subscriptions",
        db_index=True,
    )
    subscription = models.ForeignKey(
        PlanCost, on_delete=models.CASCADE, related_name="subscriptions", db_index=True
    )
    date_billing_start = models.DateTimeField(blank=True, null=True)
    date_billing_end = models.DateTimeField(blank=True, null=True)
    date_billing_last = models.DateTimeField(blank=True, null=True)
    date_billing_next = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True, db_index=True)
    cancelled = models.BooleanField(default=False)
    units_remaining = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = (
            "user",
            "date_billing_start",
        )

    def __str__(self):
        return f"{self.user.username} - {self.subscription.plan.plan_name}"

    def save(self, *args, **kwargs):
        if self.subscription.is_usage_based and self.units_remaining == 0:
            self.units_remaining = self.subscription.units_included
        super().save(*args, **kwargs)

    def decrement_units(self, units=1):
        """Decrement units for usage-based plans."""
        if self.subscription.is_usage_based:
            self.units_remaining -= units
            self.save()
            if self.units_remaining <= 0:
                self.active = False
                self.save()

    def reset_units(self):
        """Reset units when a new usage-based plan is purchased."""
        if self.subscription.is_usage_based:
            self.units_remaining = self.subscription.units_included
            self.save()


class UsageTracker(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="usage_tracker"
    )
    subscription = models.ForeignKey(
        "UserSubscription", on_delete=models.CASCADE, related_name="usage_tracker"
    )
    usage_type = models.IntegerField(choices=UsageTypeChoices.choices)

    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "subscription", "usage_type")

    def __str__(self):
        return f"{self.user.username} - {self.usage_type} - {self.usage_count}"

    def increment_usage(self, units=1):
        """Increment usage by a given number of units."""
        self.usage_count += units
        self.save()

    def is_limit_exceeded(self, limit):
        """Check if the usage limit for this type has been exceeded."""
        return self.usage_count >= limit
