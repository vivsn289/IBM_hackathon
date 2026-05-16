"""Session management."""

from auth.users import verify_password
from core.utils import log_event, now_ms


_SESSIONS = {}


def login(user_id, password):
    if not verify_password(user_id, password):
        log_event("auth_fail", {"user_id": user_id})
        return None
    token = f"sess-{user_id}-{now_ms()}"
    _SESSIONS[token] = {"user_id": user_id, "created": now_ms()}
    return token


def get_session(token):
    return _SESSIONS.get(token)


def logout(token):
    _SESSIONS.pop(token, None)
