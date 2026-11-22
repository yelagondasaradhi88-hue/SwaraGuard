"""
In-memory Mock Bank State and Event Store for Fraud Call Shield.
All data is simulated and non-sensitive for academic and hackathon demonstrations.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy


INITIAL_ACCOUNT = {
    "name": "Demo User",
    "account_no": "XXXX1234",
    "balance": 50000.0,
    "status": "ACTIVE",  # ACTIVE or FROZEN
    "frozen_until": None,  # ISO format string or None
    "callback_pending": False,
    "protected_user": True,
    "typical_max_transfer": 5000.0,
    "known_payees": ["RENT-0001", "GROCER-0002"],
    "guardian": {
        "name": "Family Guardian",
        "phone": "+91-98765-00000",
        "relationship": "Daughter"
    },
    "security_questions": [
        {
            "id": "q1",
            "question": "What is your mother's maiden name?",
            "answer": "Sharma"
        },
        {
            "id": "q2",
            "question": "What city was your first job in?",
            "answer": "Pune"
        }
    ]
}


class MockBankState:
    """Manages bank account state, telemetry window, alerts, and audit trail in memory."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Restores all state back to initial pristine configuration."""
        self.account: Dict[str, Any] = copy.deepcopy(INITIAL_ACCOUNT)
        self.session_events: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []
        self.guardian_notifications: List[Dict[str, Any]] = []
        self.pending_transfer: Optional[Dict[str, Any]] = None
        self.freeze_trigger_count: int = 0
        self.last_decision_ms: float = 0.0

        self.log_audit("SYSTEM_INIT", "Mock bank initialized with Demo User balance 50,000 INR.")

    def log_audit(self, action: str, details: Any):
        """Appends an event to the persistent session audit log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "details": details
        }
        self.audit_log.append(entry)

    def add_event(self, event_data: Dict[str, Any]):
        """Adds a device event with timestamp to the session sliding window."""
        ts = event_data.get("timestamp")
        if not ts:
            event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        elif isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            event_data["timestamp"] = ts.isoformat()

        self.session_events.append(event_data)
        self.log_audit("DEVICE_EVENT_INGESTED", {
            "type": event_data.get("event_type"),
            "details": event_data.get("details")
        })

    def check_auto_unfreeze(self, current_time: Optional[datetime] = None) -> bool:
        """Checks if frozen_until has passed and automatically unfreezes the account."""
        if self.account["status"] != "FROZEN":
            return False

        frozen_until_str = self.account.get("frozen_until")
        if not frozen_until_str:
            return False

        now = current_time or datetime.now(timezone.utc)
        frozen_until_dt = datetime.fromisoformat(frozen_until_str)
        if frozen_until_dt.tzinfo is None:
            frozen_until_dt = frozen_until_dt.replace(tzinfo=timezone.utc)

        if now >= frozen_until_dt:
            self.account["status"] = "ACTIVE"
            self.account["frozen_until"] = None
            self.account["callback_pending"] = False
            self.log_audit("AUTO_UNFREEZE", "Freeze duration elapsed (30 minutes). Account restored to ACTIVE.")
            return True
        return False

    def freeze_account(self, duration_minutes: int = 30, reasons: Optional[List[str]] = None) -> bool:
        """
        Freezes outgoing transfers for 30 minutes.
        Only executes once per session to prevent repetitive state churning.
        """
        now = datetime.now(timezone.utc)
        if self.account["status"] == "FROZEN":
            return False

        self.account["status"] = "FROZEN"
        frozen_until = now + timedelta(minutes=duration_minutes)
        self.account["frozen_until"] = frozen_until.isoformat()
        self.account["callback_pending"] = True
        self.freeze_trigger_count += 1

        alert_payload = {
            "timestamp": now.isoformat(),
            "target_user": self.account["name"],
            "account_no": self.account["account_no"],
            "guardian_phone": self.account["guardian"]["phone"],
            "action": "OUTGOING_TRANSFERS_FROZEN",
            "duration_minutes": duration_minutes,
            "reasons": reasons or ["Critical multi-factor fraud sequence detected."]
        }
        self.guardian_notifications.append(alert_payload)

        self.log_audit("ACCOUNT_FROZEN", {
            "duration": f"{duration_minutes}m",
            "reasons": reasons,
            "guardian_alerted": self.account["guardian"]["name"]
        })
        return True

    def notify_guardian(self, level: str, message: str, reasons: List[str]):
        """Dispatches simulated notification to family guardian."""
        now = datetime.now(timezone.utc)
        notification = {
            "timestamp": now.isoformat(),
            "level": level,
            "message": message,
            "guardian": self.account["guardian"],
            "reasons": reasons
        }
        self.guardian_notifications.append(notification)
        self.log_audit("GUARDIAN_NOTIFIED", notification)

    def unfreeze_account(self, actor: str = "BANK_CALLBACK"):
        """Restores account to ACTIVE status and clears pending callback & window."""
        self.account["status"] = "ACTIVE"
        self.account["frozen_until"] = None
        self.account["callback_pending"] = False
        self.pending_transfer = None
        # Clearing or archiving the current threat window
        self.session_events.clear()
        self.log_audit("ACCOUNT_UNFROZEN", f"Account unlocked by {actor}. Device session window cleared.")


# Singleton state instance
bank_state = MockBankState()
