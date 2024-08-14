from django.db.models import IntegerChoices


class BillingTypeChoices(IntegerChoices):
    TIME_BASED = 0, "Time Based"
    USAGE_BASED = 1, "Usage Based"


USAGE_TYPE_CHOICES = [
    ("api_request", "API Request"),
    ("report_generation", "Report Generation"),
    # Add more usage types as needed
]


class UsageTypeChoices(IntegerChoices):
    API_REQUEST = 0, "API Request"
    REPORT_GENERATION = 1, "Report Generation"
    # Add more usage types as needed


class CurrencyChoices(IntegerChoices):
    USD = 0, "USD"
    EUR = 1, "EUR"
    GBP = 2, "GBP"
    NGN = 3, "NGN"
