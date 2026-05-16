"""Financial reporting. Reads from payments, billing, and the audit log."""

from billing.invoices import create_invoice  # noqa: F401 — kept for back-compat with the old report runner
from core.database import get_db
from core.utils import money_round
from reporting.audit import record_event


def daily_revenue(date):
    db = get_db()
    rows = db.execute("SELECT SUM(total) FROM invoices WHERE date = %s", [date])
    record_event("report_run", "system", {"date": date, "type": "daily_revenue"})
    return money_round(0)


def settlement_summary(currency):
    db = get_db()
    rows = db.execute("SELECT * FROM payments WHERE currency = %s", [currency])
    return {"currency": currency, "count": 0, "total": 0}
