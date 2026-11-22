import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from models import (
    AccountResponse,
    AccountStatus,
    AccountType,
    StatementResponse,
    StatementSummary,
    TransactionResponse,
    TransactionStatus,
    TransferMode,
    inr_to_paise,
    paise_to_inr,
)

# Custom Exceptions for clean domain errors
class BankException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AccountNotFoundException(BankException):
    def __init__(self, account_id: str):
        super().__init__(
            code="ACCOUNT_NOT_FOUND",
            message=f"Account '{account_id}' was not found in the banking ledger.",
            status_code=404,
            details={"accountId": account_id},
        )


class AccountFrozenException(BankException):
    def __init__(self, account_id: str, is_sender: bool = True):
        role = "Sender" if is_sender else "Beneficiary"
        super().__init__(
            code="ACCOUNT_FROZEN",
            message=f"{role} account '{account_id}' is currently FROZEN (transactions halted for security).",
            status_code=403,
            details={"accountId": account_id, "status": "FROZEN"},
        )


class InsufficientFundsException(BankException):
    def __init__(self, account_id: str, available_paise: int, required_paise: int):
        super().__init__(
            code="INSUFFICIENT_FUNDS",
            message=(
                f"Available balance ₹{paise_to_inr(available_paise):,.2f} is insufficient "
                f"for transfer of ₹{paise_to_inr(required_paise):,.2f}."
            ),
            status_code=422,
            details={
                "accountId": account_id,
                "availableInr": paise_to_inr(available_paise),
                "requiredInr": paise_to_inr(required_paise),
                "shortfallInr": paise_to_inr(required_paise - available_paise),
            },
        )


class SelfTransferException(BankException):
    def __init__(self, account_id: str):
        super().__init__(
            code="SELF_TRANSFER_NOT_ALLOWED",
            message="Source account and destination account cannot be identical.",
            status_code=400,
            details={"accountId": account_id},
        )


class BankDatabase:
    """Thread-safe SQLite banking ledger with integer paise calculations and ACID guarantees."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to local mock_bank.db in the directory
            dir_name = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.getenv("MOCK_BANK_DB_PATH", os.path.join(dir_name, "mock_bank.db"))
        else:
            self.db_path = db_path

        self._lock = threading.RLock()
        self.init_schema()
        self.seed_defaults()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for concurrency and enforce foreign keys
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self):
        with self._lock, self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    holder_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    ifsc TEXT NOT NULL,
                    balance_paise INTEGER NOT NULL CHECK (balance_paise >= 0),
                    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'FROZEN')),
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    txn_id TEXT PRIMARY KEY,
                    from_account_id TEXT NOT NULL,
                    to_account_id TEXT NOT NULL,
                    amount_paise INTEGER NOT NULL CHECK (amount_paise > 0),
                    currency TEXT NOT NULL DEFAULT 'INR',
                    mode TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'PENDING')),
                    reference_note TEXT,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS idempotency_records (
                    idempotency_key TEXT PRIMARY KEY,
                    request_hash TEXT,
                    response_json TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_txn_from ON transactions(from_account_id);
                CREATE INDEX IF NOT EXISTS idx_txn_to ON transactions(to_account_id);
                CREATE INDEX IF NOT EXISTS idx_txn_timestamp ON transactions(timestamp);
            """)

    def seed_defaults(self):
        """Pre-seeds sample accounts and realistic transaction history if database is clean."""
        with self._lock, self.get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM accounts;")
            count = cur.fetchone()[0]
            if count > 0:
                return

            now_iso = datetime.now(timezone.utc).isoformat()
            sample_accounts = [
                ("ACC-IND-1001", "Saradhi Yelagonda", "SAVINGS", "MOCK0001234", 7500000, "ACTIVE", now_iso),
                ("ACC-IND-1002", "Acme Retail Tech Pvt Ltd", "CURRENT", "MOCK0001234", 25000000, "ACTIVE", now_iso),
                ("ACC-IND-1003", "Cyber Safe Emergency Reserve", "SAVINGS", "MOCK0001234", 10000000, "ACTIVE", now_iso),
            ]

            conn.executemany("""
                INSERT INTO accounts (account_id, holder_name, account_type, ifsc, balance_paise, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, sample_accounts)

            sample_transactions = [
                (
                    "TXN-INIT-001",
                    "CORP-PAYROLL-HDFC",
                    "ACC-IND-1001",
                    8500000,
                    "INR",
                    "NEFT",
                    "SUCCESS",
                    "Monthly Honorarium & Salary Credit",
                    now_iso,
                ),
                (
                    "TXN-INIT-002",
                    "ACC-IND-1001",
                    "UPI-MERCHANT-FOOD@icici",
                    145000,
                    "INR",
                    "UPI",
                    "SUCCESS",
                    "Zomato Food Order #8271",
                    now_iso,
                ),
                (
                    "TXN-INIT-003",
                    "ACC-IND-1001",
                    "ACC-IND-1002",
                    855000,
                    "INR",
                    "INTERNAL",
                    "SUCCESS",
                    "SwaraGuard Cloud AI Subscription",
                    now_iso,
                ),
            ]

            conn.executemany("""
                INSERT INTO transactions (txn_id, from_account_id, to_account_id, amount_paise, currency, mode, status, reference_note, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, sample_transactions)

    # --- Account Methods ---

    def create_account(
        self,
        holder_name: str,
        account_type: AccountType,
        ifsc: str = "MOCK0001234",
        initial_deposit_inr: float = 0.0,
    ) -> AccountResponse:
        with self._lock, self.get_connection() as conn:
            account_id = f"ACC-IND-{uuid.uuid4().hex[:8].upper()}"
            paise = inr_to_paise(initial_deposit_inr)
            created_at = datetime.now(timezone.utc).isoformat()
            status = "ACTIVE"

            conn.execute("""
                INSERT INTO accounts (account_id, holder_name, account_type, ifsc, balance_paise, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (account_id, holder_name, account_type.value, ifsc, paise, status, created_at))

            if paise > 0:
                txn_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
                conn.execute("""
                    INSERT INTO transactions (txn_id, from_account_id, to_account_id, amount_paise, currency, mode, status, reference_note, timestamp)
                    VALUES (?, ?, ?, ?, 'INR', 'INTERNAL', 'SUCCESS', 'Initial Account Opening Deposit', ?);
                """, (txn_id, "SYSTEM-TREASURY", account_id, paise, created_at))

            return AccountResponse(
                accountId=account_id,
                holderName=holder_name,
                accountType=account_type,
                ifsc=ifsc,
                balance=paise_to_inr(paise),
                balancePaise=paise,
                status=AccountStatus(status),
                createdAt=created_at,
            )

    def get_account(self, account_id: str) -> AccountResponse:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM accounts WHERE account_id = ?;", (account_id,)).fetchone()
            if not row:
                raise AccountNotFoundException(account_id)

            return AccountResponse(
                accountId=row["account_id"],
                holderName=row["holder_name"],
                accountType=AccountType(row["account_type"]),
                ifsc=row["ifsc"],
                balance=paise_to_inr(row["balance_paise"]),
                balancePaise=row["balance_paise"],
                status=AccountStatus(row["status"]),
                createdAt=row["created_at"],
            )

    def set_account_status(self, account_id: str, new_status: AccountStatus) -> AccountResponse:
        with self._lock, self.get_connection() as conn:
            # Check existence
            row = conn.execute("SELECT * FROM accounts WHERE account_id = ?;", (account_id,)).fetchone()
            if not row:
                raise AccountNotFoundException(account_id)

            conn.execute("UPDATE accounts SET status = ? WHERE account_id = ?;", (new_status.value, account_id))

        return self.get_account(account_id)

    # --- Transfer & Statement Methods ---

    def execute_transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount_inr: float,
        mode: TransferMode = TransferMode.INTERNAL,
        reference_note: Optional[str] = "Transfer",
    ) -> TransactionResponse:
        """Atomic transfer of funds between two accounts using SQLite transactions."""
        if from_account_id == to_account_id:
            raise SelfTransferException(from_account_id)

        amount_paise = inr_to_paise(amount_inr)
        if amount_paise <= 0:
            raise BankException("INVALID_AMOUNT", "Transfer amount must be positive.", 400)

        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE;")

            # 1. Fetch sender
            from_row = cursor.execute("SELECT * FROM accounts WHERE account_id = ?;", (from_account_id,)).fetchone()
            if not from_row:
                cursor.execute("ROLLBACK;")
                raise AccountNotFoundException(from_account_id)

            if from_row["status"] == "FROZEN":
                cursor.execute("ROLLBACK;")
                raise AccountFrozenException(from_account_id, is_sender=True)

            # 2. Fetch receiver
            to_row = cursor.execute("SELECT * FROM accounts WHERE account_id = ?;", (to_account_id,)).fetchone()
            if not to_row:
                cursor.execute("ROLLBACK;")
                raise AccountNotFoundException(to_account_id)

            if to_row["status"] == "FROZEN":
                cursor.execute("ROLLBACK;")
                raise AccountFrozenException(to_account_id, is_sender=False)

            # 3. Check Balance
            sender_balance = from_row["balance_paise"]
            if sender_balance < amount_paise:
                cursor.execute("ROLLBACK;")
                raise InsufficientFundsException(from_account_id, sender_balance, amount_paise)

            # 4. Atomic Balance Update
            new_sender_bal = sender_balance - amount_paise
            new_receiver_bal = to_row["balance_paise"] + amount_paise

            cursor.execute("UPDATE accounts SET balance_paise = ? WHERE account_id = ?;", (new_sender_bal, from_account_id))
            cursor.execute("UPDATE accounts SET balance_paise = ? WHERE account_id = ?;", (new_receiver_bal, to_account_id))

            # 5. Insert Transaction Log
            txn_id = f"TXN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            now_iso = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO transactions (txn_id, from_account_id, to_account_id, amount_paise, currency, mode, status, reference_note, timestamp)
                VALUES (?, ?, ?, ?, 'INR', ?, 'SUCCESS', ?, ?);
            """, (txn_id, from_account_id, to_account_id, amount_paise, mode.value, reference_note, now_iso))

            conn.commit()

            return TransactionResponse(
                txnId=txn_id,
                fromAccountId=from_account_id,
                toAccountId=to_account_id,
                amount=amount_inr,
                amountPaise=amount_paise,
                currency="INR",
                mode=mode,
                status=TransactionStatus.SUCCESS,
                referenceNote=reference_note,
                timestamp=now_iso,
            )

    def get_statement(
        self,
        account_id: str,
        mode: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> StatementResponse:
        account = self.get_account(account_id)

        query = """
            SELECT * FROM transactions
            WHERE (from_account_id = ? OR to_account_id = ?)
        """
        params: List[Any] = [account_id, account_id]

        if mode:
            query += " AND mode = ?"
            params.append(mode.upper())

        if from_date:
            query += " AND timestamp >= ?"
            params.append(from_date)

        if to_date:
            query += " AND timestamp <= ?"
            params.append(to_date)

        with self.get_connection() as conn:
            # Total count query
            count_query = f"SELECT COUNT(*) FROM ({query});"
            total_count = conn.execute(count_query, params).fetchone()[0]

            # Paginated query
            paginated_query = query + " ORDER BY timestamp DESC LIMIT ? OFFSET ?;"
            params_paged = list(params) + [limit, offset]
            rows = conn.execute(paginated_query, params_paged).fetchall()

            txns: List[TransactionResponse] = []
            total_credits_paise = 0
            total_debits_paise = 0

            # Compute summary over all matching transactions
            all_rows = conn.execute(query, params).fetchall()
            for r in all_rows:
                if r["status"] == "SUCCESS":
                    if r["to_account_id"] == account_id:
                        total_credits_paise += r["amount_paise"]
                    if r["from_account_id"] == account_id:
                        total_debits_paise += r["amount_paise"]

            for r in rows:
                txns.append(
                    TransactionResponse(
                        txnId=r["txn_id"],
                        fromAccountId=r["from_account_id"],
                        toAccountId=r["to_account_id"],
                        amount=paise_to_inr(r["amount_paise"]),
                        amountPaise=r["amount_paise"],
                        currency=r["currency"],
                        mode=TransferMode(r["mode"]),
                        status=TransactionStatus(r["status"]),
                        referenceNote=r["reference_note"],
                        timestamp=r["timestamp"],
                    )
                )

            summary = StatementSummary(
                totalCreditsInr=paise_to_inr(total_credits_paise),
                totalDebitsInr=paise_to_inr(total_debits_paise),
                netFlowInr=paise_to_inr(total_credits_paise - total_debits_paise),
            )

            return StatementResponse(
                accountId=account.accountId,
                holderName=account.holderName,
                currentBalance=account.balance,
                totalTransactions=total_count,
                limit=limit,
                offset=offset,
                transactions=txns,
                summary=summary,
            )

    # --- Idempotency Cache ---

    def get_idempotency_record(self, key: str) -> Optional[Tuple[int, Dict[str, Any]]]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT status_code, response_json FROM idempotency_records WHERE idempotency_key = ?;", (key,)).fetchone()
            if row:
                return row["status_code"], json.loads(row["response_json"])
            return None

    def save_idempotency_record(self, key: str, status_code: int, response_data: Dict[str, Any]):
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO idempotency_records (idempotency_key, response_json, status_code, created_at)
                VALUES (?, ?, ?, ?);
            """, (key, json.dumps(response_data), status_code, now_iso))
