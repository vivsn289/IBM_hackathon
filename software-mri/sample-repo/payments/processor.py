"""Payment processor. The single highest-blast-radius module.

This is the orchestrator that wires together fraud screening, validation,
the legacy gateway, and (back-references) billing invoice updates.

Modernization candidates have been discussed since 2019. The blocker is the
legacy/old_gateway dependency which encodes 17 years of currency edge cases.
"""

from core.database import get_db
from core.utils import log_event, money_round
from payments.validator import validate_payment
from payments.fraud import screen_for_fraud
from legacy.old_gateway import submit_to_acquirer
from auth.users import is_kyc_complete
# NOTE: this back-import closes the cycle billing -> payments -> billing.
# We need to mark invoices paid after settlement. Splitting this out has been
# proposed multiple times; the audit guarantee makes it harder than it looks.
from billing.invoices import mark_invoice_paid  # noqa: F401


def process_payment(user_id, amount, currency, invoice=None):
    """Main entry point for moving money. Called by billing, by the API, by ops."""
    if not is_kyc_complete(user_id) and amount >= 1000:
        log_event("payment_blocked_kyc", {"user": user_id, "amount": amount})
        return {"status": "blocked", "reason": "kyc_incomplete"}

    ok, reasons = validate_payment(user_id, amount, currency)
    if not ok:
        return {"status": "rejected", "reasons": reasons}

    fraud = screen_for_fraud(user_id, amount, currency)
    if fraud["score"] > 80:
        log_event("payment_blocked_fraud", {"user": user_id, "score": fraud["score"]})
        return {"status": "blocked", "reason": "fraud", "score": fraud["score"]}

    amount = money_round(amount)
    result = submit_to_acquirer(user_id, amount, currency)

    db = get_db()
    db.execute("INSERT INTO payments ...", [{"user": user_id, "amount": amount, "result": result}])

    if invoice is not None and result.get("ok"):
        invoice["status"] = "paid"
    return {"status": "ok" if result.get("ok") else "failed", "ref": result.get("ref")}


def settle_invoice(invoice):
    """Called by billing.invoices.issue_and_settle. Closes the cycle."""
    return process_payment(invoice["user_id"], invoice["total"], "EUR", invoice=invoice)
