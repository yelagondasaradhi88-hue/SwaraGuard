# 🏦 SwaraGuard Mock Retail Bank API (INR ₹)

A production-grade, lightweight mock retail banking service tailored for **SwaraGuard** to simulate real-world Indian banking flows in INR (₹). It features **zero floating-point drift** (using internal integer paise math), **atomic database transactions**, **idempotency caching**, **scam emergency freeze**, and **network resilience simulation flags**.

---

## ⚡ Key Highlights

1. **Exact Currency Representation (Zero Floating-Point Drift)**:
   - All balances and transactions are stored internally as integer **paise** (1 INR = 100 paise).
   - E.g., `₹75,000.50` is stored as `7500050` paise and computed with decimal precision.
2. **ACID Atomic Transfers**:
   - Transfers use SQLite `BEGIN IMMEDIATE` transactions to guarantee sender debit and recipient credit execute atomically.
3. **Idempotency Protection**:
   - Supports `Idempotency-Key` HTTP header. Retries return cached responses with header `X-Cache-Lookup: HIT`, preventing double-debits.
4. **Emergency Account Freezing**:
   - Supports `FROZEN` account status. Blocked accounts reject incoming and outgoing transfers (returns `403 ACCOUNT_FROZEN`).
5. **Resilience Testing**:
   - Header `X-Simulate-Failure: true` (or `?simulate_failure=true`) simulates bank switch gateway timeouts (`503`).
   - Header `X-Simulate-Delay: <ms>` simulates network latency.
6. **Pre-Seeded Sample Accounts**:
   - Pre-loaded with ready-to-test accounts and realistic transaction histories (UPI, NEFT, IMPS).

---

## 📦 Directory Structure

```
mock-bank-api/
├── README.md           # Documentation & curl examples
├── requirements.txt    # Minimal dependencies (FastAPI, Uvicorn, Pydantic, pytest)
├── app.py              # FastAPI application, routes, and error middleware
├── models.py           # Pydantic data schemas, enums, and paise conversion helpers
├── database.py         # SQLite ledger with thread-safe connection and atomic transactions
└── test_api.py         # Comprehensive Pytest test suite (13 passing tests)
```

---

## 🚀 Quickstart

### 1. Run the Server
From the project root:
```bash
cd mock-bank-api
uvicorn app:app --port 8001 --reload
```
Interactive Swagger Documentation will be available at: **`http://localhost:8001/docs`**

### 2. Run the Test Suite
```bash
pytest test_api.py -v
```

---

## 🏛️ Pre-Seeded Sample Accounts

| Account ID | Holder Name | Type | IFSC | Starting Balance | Status |
|---|---|---|---|---|---|
| `ACC-IND-1001` | **Saradhi Yelagonda** | `SAVINGS` | `MOCK0001234` | **₹75,000.00** | `ACTIVE` |
| `ACC-IND-1002` | **Acme Retail Tech Pvt Ltd** | `CURRENT` | `MOCK0001234` | **₹2,50,000.00** | `ACTIVE` |
| `ACC-IND-1003` | **Cyber Safe Emergency Reserve** | `SAVINGS` | `MOCK0001234` | **₹1,00,000.00** | `ACTIVE` |

---

## 📖 API Endpoints & Curl Examples

### 1. Create a New Bank Account
**`POST /api/accounts`**
```bash
curl -X POST http://localhost:8001/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "holderName": "Vikram Adiga",
    "accountType": "SAVINGS",
    "ifsc": "MOCK0001234",
    "initialDeposit": 15000.00
  }'
```
**Response (201 Created):**
```json
{
  "accountId": "ACC-IND-9B3E2A10",
  "holderName": "Vikram Adiga",
  "accountType": "SAVINGS",
  "ifsc": "MOCK0001234",
  "balance": 15000.0,
  "balancePaise": 1500000,
  "status": "ACTIVE",
  "createdAt": "2026-11-21T17:28:10.123456+00:00"
}
```

---

### 2. Fetch Account Details & Balance
**`GET /api/accounts/{accountId}`**
```bash
curl http://localhost:8001/api/accounts/ACC-IND-1001
```
**Response (200 OK):**
```json
{
  "accountId": "ACC-IND-1001",
  "holderName": "Saradhi Yelagonda",
  "accountType": "SAVINGS",
  "ifsc": "MOCK0001234",
  "balance": 75000.0,
  "balancePaise": 7500000,
  "status": "ACTIVE",
  "createdAt": "2026-11-21T17:00:00+00:00"
}
```

---

### 3. Transfer Funds Atomically (With Idempotency Key)
**`POST /api/transfers`**
```bash
curl -X POST http://localhost:8001/api/transfers \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: TXN-REQ-987654321" \
  -d '{
    "fromAccountId": "ACC-IND-1001",
    "toAccountId": "ACC-IND-1002",
    "amount": 2500.50,
    "mode": "UPI",
    "referenceNote": "SwaraGuard API monthly tier"
  }'
```
**Response (200 OK):**
```json
{
  "txnId": "TXN-20261121-C8A4B291",
  "fromAccountId": "ACC-IND-1001",
  "toAccountId": "ACC-IND-1002",
  "amount": 2500.5,
  "amountPaise": 250050,
  "currency": "INR",
  "mode": "UPI",
  "status": "SUCCESS",
  "referenceNote": "SwaraGuard API monthly tier",
  "timestamp": "2026-11-21T17:29:45.678901+00:00"
}
```
*Note: If you run this exact curl command again with the same `Idempotency-Key`, it returns the same transaction with header `X-Cache-Lookup: HIT` without debiting the account again.*

---

### 4. Paginated Account Statement with Filters
**`GET /api/accounts/{accountId}/statement?limit=5&offset=0&mode=UPI`**
```bash
curl "http://localhost:8001/api/accounts/ACC-IND-1001/statement?limit=5&offset=0"
```
**Response (200 OK):**
```json
{
  "accountId": "ACC-IND-1001",
  "holderName": "Saradhi Yelagonda",
  "currentBalance": 72499.5,
  "totalTransactions": 4,
  "limit": 5,
  "offset": 0,
  "transactions": [
    {
      "txnId": "TXN-20261121-C8A4B291",
      "fromAccountId": "ACC-IND-1001",
      "toAccountId": "ACC-IND-1002",
      "amount": 2500.5,
      "amountPaise": 250050,
      "currency": "INR",
      "mode": "UPI",
      "status": "SUCCESS",
      "referenceNote": "SwaraGuard API monthly tier",
      "timestamp": "2026-11-21T17:29:45.678901+00:00"
    }
  ],
  "summary": {
    "totalCreditsInr": 85000.0,
    "totalDebitsInr": 12500.5,
    "netFlowInr": 72499.5
  }
}
```

---

### 5. Emergency Account Freeze (Anti-Scam Defense)
**`POST /api/accounts/{accountId}/freeze`**
```bash
curl -X POST http://localhost:8001/api/accounts/ACC-IND-1001/freeze \
  -H "Content-Type: application/json" \
  -d '{"reason": "SwaraGuard flagged high-risk deepfake voice scam"}'
```
**Response (200 OK):**
```json
{
  "accountId": "ACC-IND-1001",
  "holderName": "Saradhi Yelagonda",
  "accountType": "SAVINGS",
  "ifsc": "MOCK0001234",
  "balance": 72499.5,
  "balancePaise": 7249950,
  "status": "FROZEN",
  "createdAt": "2026-11-21T17:00:00+00:00"
}
```
*Any transfer attempt while frozen will immediately be rejected:*
```json
{
  "error": {
    "code": "ACCOUNT_FROZEN",
    "message": "Sender account 'ACC-IND-1001' is currently FROZEN (transactions halted for security).",
    "details": {
      "accountId": "ACC-IND-1001",
      "status": "FROZEN"
    }
  }
}
```

To unfreeze:
```bash
curl -X POST http://localhost:8001/api/accounts/ACC-IND-1001/unfreeze
```

---

### 6. Resilience & Transient Failure Simulation
To test client retry logic and circuit breakers:
```bash
curl -X POST http://localhost:8001/api/transfers \
  -H "Content-Type: application/json" \
  -H "X-Simulate-Failure: true" \
  -d '{
    "fromAccountId": "ACC-IND-1001",
    "toAccountId": "ACC-IND-1002",
    "amount": 500.0
  }'
```
**Response (503 Service Unavailable):**
```json
{
  "error": {
    "code": "SIMULATED_TRANSIENT_FAILURE",
    "message": "Simulated bank switch gateway timeout. Please retry with Idempotency-Key.",
    "details": {
      "simulated": true,
      "network": "INTERNAL"
    }
  }
}
```

---

## 🛡️ Integration with SwaraGuard Workspace
The Mock Bank API can be wired directly with SwaraGuard's **Emergency Freeze Panel** (in `index.html`) by pointing the frontend freeze request to `/api/accounts/{accountId}/freeze` to simulate real-time banking protection when scam audio is detected.
