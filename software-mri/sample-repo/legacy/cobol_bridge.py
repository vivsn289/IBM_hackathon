"""COBOL bridge. Calls the mainframe over a socket protocol from 1998.

The mainframe team retires in waves. The last person who can read the
CICS transaction definitions retires in 2026. This is the single largest
modernization-blocker in the system.
"""

from core.utils import log_event


def call_legacy_settlement(user_id, amount, currency):
    # In prod: open a socket to the mainframe gateway, format an EBCDIC fixed-width
    # record, await response, decode. Stubbed for the demo.
    log_event("cobol_call", {"user": user_id, "amount": amount, "currency": currency})
    return {
        "ok": True,
        "ref": f"COBOL-{user_id}-{currency}",
        "amount_settled": amount,
        "settlement_lag_days": 42,  # post-Brexit GBP path
    }
