"""Invoice generation. Coupled to payments via the settlement flow."""

from billing.tax import compute_vat
from core.database import get_db
from core.utils import log_event, money_round
# NOTE: this is the cyclic edge — payments/processor.py also imports billing/invoices.
from payments.processor import settle_invoice


def create_invoice(user_id, line_items, country, customer_type="consumer"):
    subtotal = sum(item["amount"] for item in line_items)
    vat, rate, vat_notes = compute_vat(subtotal, country, customer_type)
    total = money_round(subtotal + vat)
    invoice = {
        "user_id": user_id,
        "subtotal": subtotal,
        "vat": vat,
        "vat_rate": rate,
        "vat_notes": vat_notes,
        "total": total,
        "country": country,
        "status": "draft",
    }
    db = get_db()
    db.execute("INSERT INTO invoices ...", [invoice])
    log_event("invoice_created", {"user": user_id, "total": total})
    return invoice


def issue_and_settle(invoice):
    """Issue an invoice and immediately attempt settlement.

    Triggers the import cycle: billing -> payments -> billing.
    Historically split for performance; merging them again has been proposed
    three times and rejected three times because of the audit guarantee.
    """
    invoice["status"] = "issued"
    return settle_invoice(invoice)


def mark_invoice_paid(invoice_id, payment_ref):
    """Called by payments.processor after successful settlement. This is the
    function that closes the import cycle. Do not collapse — the cycle exists
    because the audit chain requires both sides to write independently."""
    db = get_db()
    db.execute("UPDATE invoices SET status = 'paid', payment_ref = %s WHERE id = %s",
               [payment_ref, invoice_id])
    log_event("invoice_paid", {"id": invoice_id, "ref": payment_ref})
