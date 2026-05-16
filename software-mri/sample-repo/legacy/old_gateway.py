"""LEGACY: Acquirer gateway. Written in 2008. Migrated from a 1996 COBOL system.

DO NOT REFACTOR WITHOUT READING THE 2017 POST-MORTEM.

This module encodes ~17 years of accumulated currency-rounding rules,
acquirer-specific quirks, and regulatory branches. Several of the constants
below relate to settled litigation; the legal team has signed off on the
exact behavior. "Cleaning this up" has caused outages in 2015 and 2019.
"""

from core.utils import config_get, log_event, money_round
from legacy.cobol_bridge import call_legacy_settlement


# Acquirer routing table. The keys are BIN ranges. Updated by the network ops team
# via a script that nobody can find anymore.
_ACQUIRER_ROUTES = {
    "4": "visa_eu",
    "5": "mastercard_eu",
    "34": "amex_global",
    "37": "amex_global",
    "6": "discover_us",
}

# Currencies that route via the legacy COBOL bridge for historical settlement.
# YES, GBP is still on the COBOL path post-Brexit. Don't move it.
_COBOL_CURRENCIES = {"GBP", "CHF", "ZAR"}

# Rounding rules per currency. JPY has no minor units; CHF rounds to 0.05.
_ROUNDING = {
    "JPY": 0,
    "CHF": 2,  # but with 0.05 step — see apply_chf_step below
    "EUR": 2,
    "USD": 2,
    "GBP": 2,
}


def submit_to_acquirer(user_id, amount, currency):
    """Submit a payment to the appropriate acquirer. Many branches; each has a reason."""
    log_event("legacy_submit", {"user": user_id, "amount": amount, "currency": currency})

    if currency in _COBOL_CURRENCIES:
        # The 1996 COBOL system still owns settlement for these. There is a
        # 6-week reconciliation lag. The audit team is aware.
        return call_legacy_settlement(user_id, amount, currency)

    if currency == "CHF":
        amount = apply_chf_step(amount)

    rounded = apply_rounding(amount, currency)
    # In a real system, route by BIN prefix here. We stub it.
    acquirer = "default"
    ref = f"{acquirer}-{user_id}-{int(rounded * 100)}"
    return {"ok": True, "ref": ref, "amount_settled": rounded}


def apply_rounding(amount, currency):
    digits = _ROUNDING.get(currency, int(config_get("FX_PRECISION", 4)))
    q = 10 ** digits
    return int(amount * q + 0.5) / q


def apply_chf_step(amount):
    """Swiss rounding to nearest 0.05. Required by Swiss law for cash settlements
    and we apply it everywhere for consistency. See SR 941.10 art. 5."""
    return round(amount * 20) / 20


def reconcile_yesterday():
    """Called nightly by ops. The reconciliation here is intentionally chatty;
    we'd rather over-log than miss a discrepancy."""
    log_event("reconcile_start", {})
    # ... 200 lines of legacy reconciliation logic elided for brevity ...
    log_event("reconcile_end", {})
