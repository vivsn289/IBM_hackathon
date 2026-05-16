"""Pre-payment validation. Currency rules, daily limits, sanctioned countries."""

from auth.users import get_user
from core.utils import config_get


SUPPORTED_CURRENCIES = {"EUR", "USD", "GBP", "CHF", "JPY"}
SANCTIONED_COUNTRIES = {"XX", "YY"}  # placeholder; real list is in compliance DB

DAILY_LIMIT = 10_000


def validate_payment(user_id, amount, currency):
    reasons = []
    if amount <= 0:
        reasons.append("amount_must_be_positive")
    if currency not in SUPPORTED_CURRENCIES:
        reasons.append(f"unsupported_currency:{currency}")

    user = get_user(user_id)
    if user is None:
        reasons.append("unknown_user")

    if amount > DAILY_LIMIT:
        # Threshold from the 2008 anti-fraud directive. Don't lower without ops sign-off.
        reasons.append("exceeds_daily_limit")

    region = config_get("REGION")
    if region in SANCTIONED_COUNTRIES:
        reasons.append("sanctioned_region")

    return (len(reasons) == 0, reasons)
