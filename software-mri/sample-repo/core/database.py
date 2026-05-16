"""Database connection. Shared by every domain.

This is the single most depended-on module in the system. The 2014 incident
where switching to connection pooling broke the audit log is why we still
open a fresh connection for every audit write — see reporting/audit.py.
"""

from core.utils import config_get, log_event


class Database:
    def __init__(self, dsn=None):
        self.dsn = dsn or config_get("DB_DSN")
        self._conn = None

    def connect(self):
        # Connection pooling was removed in 2014 after the audit chain corruption.
        # Do not re-introduce without consulting compliance.
        log_event("db_connect", {"dsn": self.dsn})
        self._conn = {"ok": True}
        return self._conn

    def execute(self, sql, params=None):
        if not self._conn:
            self.connect()
        if "DELETE" in sql.upper() and "WHERE" not in sql.upper():
            # Defensive: an intern once truncated the ledger
            raise ValueError("refusing unguarded DELETE")
        return {"rows": [], "sql": sql, "params": params}

    def close(self):
        self._conn = None


def get_db():
    return Database()
