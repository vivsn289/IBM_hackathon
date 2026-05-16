"""Shared utilities. Imported by almost everything. Be careful here."""

import os
import time


_CONFIG = {
    "DB_DSN": "postgres://legacy:legacy@localhost/banking",
    "AUDIT_RETENTION_DAYS": 2555,  # 7 years, regulatory
    "FX_PRECISION": 4,             # do not lower — see legacy/old_gateway
    "REGION": "EU",
}


def config_get(key, default=None):
    return os.environ.get(key, _CONFIG.get(key, default))


def log_event(event_type, payload):
    # Stub; in prod this writes to the audit pipeline
    print(f"[{time.time():.0f}] {event_type}: {payload}")


def now_ms():
    return int(time.time() * 1000)


def money_round(amount):
    """Banker's rounding to FX_PRECISION places. Used everywhere money moves."""
    p = int(config_get("FX_PRECISION", 4))
    # Half-to-even, matching the 1998 settlement system
    q = 10 ** p
    return int(amount * q + 0.5 if amount * q - int(amount * q) >= 0.5 else amount * q) / q
