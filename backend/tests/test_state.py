"""
Tests for demo state / bank freeze behavior.
"""
from backend.api.state import demo_state, TransactionLock


def test_freeze_account_sets_status():
    demo_state.account["status"] = "FROZEN"
    lock = TransactionLock(account_alias="XXXX1234", reason="Scam detected", duration_minutes=1440)
    demo_state.active_lock = lock
    assert demo_state.account["status"] == "FROZEN"
    assert demo_state.active_lock is not None
    assert demo_state.active_lock.status == "LOCKED"


def test_reset_clears_state():
    demo_state.account["status"] = "FROZEN"
    demo_state.active_lock = TransactionLock()
    demo_state.reset()
    assert demo_state.account["status"] == "ACTIVE"
    assert demo_state.active_lock is None
