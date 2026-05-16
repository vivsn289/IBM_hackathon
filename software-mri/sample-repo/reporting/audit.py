"""Immutable audit log. Regulatory: 7-year retention.

Always opens a fresh DB connection — this is *intentional*. See the comment
in core/database.py. The 2014 connection-pool incident corrupted the audit
chain by reusing a connection mid-transaction.
"""

from core.database import Database
from core.utils import config_get, now_ms


def record_event(event_type, actor, details):
    """Write an audit row. Never batched. Never deferred."""
    db = Database()  # fresh connection — see module docstring
    db.execute(
        "INSERT INTO audit_log (ts, type, actor, details) VALUES (%s, %s, %s, %s)",
        [now_ms(), event_type, actor, str(details)],
    )
    db.close()


def retention_days():
    return int(config_get("AUDIT_RETENTION_DAYS", 2555))
