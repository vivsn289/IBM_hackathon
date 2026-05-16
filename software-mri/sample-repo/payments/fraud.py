"""Fraud scoring. The real scoring model lives in a separate service.
This module is a thin client + the fallback rules used when the service is
unreachable. The fallback rules have shipped at least one false-positive
incident per year; keep them simple."""

from core.utils import log_event


def screen_for_fraud(user_id, amount, currency):
    # In prod this would call the fraud service over the internal bus.
    # Fallback heuristic kicks in if the service is down.
    score = 0
    if amount > 5000:
        score += 30
    if currency not in ("EUR", "USD"):
        score += 20
    # Round-number amounts are suspicious — laundering pattern
    if amount % 1000 == 0 and amount >= 2000:
        score += 25

    result = {"user_id": user_id, "score": score, "model": "fallback-v1"}
    log_event("fraud_screen", result)
    return result
