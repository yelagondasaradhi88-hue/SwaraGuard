"""
In-memory demo state for the SwaraGuard backend.
Everything here is simulated — no real bank is contacted.
"""
from datetime import datetime, timedelta, timezone


class TransactionLock:
    """A simulated outgoing-transaction lock with an expiry time."""

    def __init__(self, account_alias: str = "Primary Bank Account (XXXX1234)",
                 reason: str = "Possible scam activity detected",
                 duration_minutes: int = 15):
        self.account_alias = account_alias
        self.reason = reason
        self.duration_minutes = duration_minutes
        self.status = "LOCKED"
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)


class DemoState:
    """All mutable demo values the API reads and writes."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.account = {
            "name": "Demo User",
            "account_number": "XXXX1234",
            "balance": 125000.0,
            "status": "ACTIVE",
            "currency": "INR",
        }
        self.active_lock = None
        self.current_risk_score = 0.0
        self.current_risk_level = "LOW"
        self.guardian_alerts = []
        self.audit_log = []

    def add_audit_event(self, event_type: str, description: str, risk_score: float = None):
        self.audit_log.append({
            "event_type": event_type,
            "description": description,
            "risk_score": risk_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


demo_state = DemoState()
