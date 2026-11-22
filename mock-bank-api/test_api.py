import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Use a temporary clean database for isolated testing
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["MOCK_BANK_DB_PATH"] = temp_db.name

from app import app
from database import BankDatabase

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    # Fresh database per test run if needed
    yield


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["currency"] == "INR (₹)"
    assert data["status"] == "ONLINE"


def test_seed_accounts_exist():
    res = client.get("/api/accounts/ACC-IND-1001")
    assert res.status_code == 200
    acc = res.json()
    assert acc["accountId"] == "ACC-IND-1001"
    assert acc["holderName"] == "Saradhi Yelagonda"
    assert acc["balance"] == 75000.0
    assert acc["balancePaise"] == 7500000
    assert acc["status"] == "ACTIVE"


def test_create_account_zero_deposit():
    payload = {
        "holderName": "Rohan Sharma",
        "accountType": "SAVINGS",
        "ifsc": "MOCK0001234",
        "initialDeposit": 0.0,
    }
    res = client.post("/api/accounts", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["holderName"] == "Rohan Sharma"
    assert data["balance"] == 0.0
    assert data["balancePaise"] == 0
    assert data["status"] == "ACTIVE"


def test_create_account_with_deposit():
    payload = {
        "holderName": "Ananya Reddy",
        "accountType": "CURRENT",
        "initialDeposit": 12500.50,
    }
    res = client.post("/api/accounts", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["balance"] == 12500.50
    assert data["balancePaise"] == 1250050


def test_get_nonexistent_account_returns_404():
    res = client.get("/api/accounts/ACC-NON-EXISTENT")
    assert res.status_code == 404
    err = res.json()
    assert err["error"]["code"] == "ACCOUNT_NOT_FOUND"


def test_atomic_transfer_success():
    # Initial balance: ACC-IND-1001 = 75,000, ACC-IND-1002 = 250,000
    transfer_payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": 5000.0,
        "mode": "UPI",
        "referenceNote": "Dinner split reimbursement",
    }
    res = client.post("/api/transfers", json=transfer_payload)
    assert res.status_code == 200
    txn = res.json()
    assert txn["status"] == "SUCCESS"
    assert txn["amount"] == 5000.0
    assert txn["amountPaise"] == 500000

    # Verify balances updated atomically without float drift
    acc1 = client.get("/api/accounts/ACC-IND-1001").json()
    acc2 = client.get("/api/accounts/ACC-IND-1002").json()
    assert acc1["balance"] == 70000.0
    assert acc1["balancePaise"] == 7000000
    assert acc2["balance"] == 255000.0
    assert acc2["balancePaise"] == 25500000


def test_reject_self_transfer():
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1001",
        "amount": 500.0,
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 400
    err = res.json()
    assert err["error"]["code"] == "SELF_TRANSFER_NOT_ALLOWED"


def test_reject_non_positive_amount():
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": -100.0,
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 422
    err = res.json()
    assert err["error"]["code"] == "VALIDATION_ERROR"


def test_reject_insufficient_funds():
    # Balance is 70,000. Attempt 99,999,999
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": 99999999.0,
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 422
    err = res.json()
    assert err["error"]["code"] == "INSUFFICIENT_FUNDS"
    assert "availableInr" in err["error"]["details"]


def test_idempotency_prevents_double_debit():
    key = "IDEM-TEST-KEY-778899"
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": 1000.0,
        "mode": "IMPS",
        "referenceNote": "One-time vendor token fee",
    }
    headers = {"Idempotency-Key": key}

    # First attempt: should execute and debit
    res1 = client.post("/api/transfers", json=payload, headers=headers)
    assert res1.status_code == 200
    txn1 = res1.json()

    bal_after_first = client.get("/api/accounts/ACC-IND-1001").json()["balance"]

    # Second attempt with identical idempotency key: must NOT double-debit!
    res2 = client.post("/api/transfers", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.headers.get("X-Cache-Lookup") == "HIT"
    txn2 = res2.json()
    assert txn1["txnId"] == txn2["txnId"]

    # Balance must remain unchanged
    bal_after_second = client.get("/api/accounts/ACC-IND-1001").json()["balance"]
    assert bal_after_second == bal_after_first


def test_freeze_account_enforcement():
    # Freeze ACC-IND-1001
    f_res = client.post("/api/accounts/ACC-IND-1001/freeze")
    assert f_res.status_code == 200
    assert f_res.json()["status"] == "FROZEN"

    # Transfer from frozen account should fail with 403
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": 500.0,
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ACCOUNT_FROZEN"

    # Transfer to frozen account should also fail with 403
    payload_incoming = {
        "fromAccountId": "ACC-IND-1002",
        "toAccountId": "ACC-IND-1001",
        "amount": 500.0,
    }
    res_incoming = client.post("/api/transfers", json=payload_incoming)
    assert res_incoming.status_code == 403
    assert res_incoming.json()["error"]["code"] == "ACCOUNT_FROZEN"

    # Unfreeze and verify transfers work again
    uf_res = client.post("/api/accounts/ACC-IND-1001/unfreeze")
    assert uf_res.status_code == 200
    assert uf_res.json()["status"] == "ACTIVE"

    res_retry = client.post("/api/transfers", json=payload)
    assert res_retry.status_code == 200


def test_simulate_transient_failure():
    payload = {
        "fromAccountId": "ACC-IND-1001",
        "toAccountId": "ACC-IND-1002",
        "amount": 250.0,
    }
    headers = {"X-Simulate-Failure": "true"}
    res = client.post("/api/transfers", json=payload, headers=headers)
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "SIMULATED_TRANSIENT_FAILURE"

    # Query param variation
    res_query = client.post("/api/transfers?simulate_failure=true", json=payload)
    assert res_query.status_code == 503
    assert res_query.json()["error"]["code"] == "SIMULATED_TRANSIENT_FAILURE"


def test_statement_pagination_and_summary():
    res = client.get("/api/accounts/ACC-IND-1001/statement?limit=5&offset=0")
    assert res.status_code == 200
    stmt = res.json()
    assert stmt["accountId"] == "ACC-IND-1001"
    assert stmt["limit"] == 5
    assert stmt["offset"] == 0
    assert len(stmt["transactions"]) > 0
    assert "summary" in stmt
    assert "totalCreditsInr" in stmt["summary"]
    assert "totalDebitsInr" in stmt["summary"]
    assert "netFlowInr" in stmt["summary"]
