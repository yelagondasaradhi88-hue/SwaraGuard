from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"


class TransferMode(str, Enum):
    UPI = "UPI"
    IMPS = "IMPS"
    NEFT = "NEFT"
    INTERNAL = "INTERNAL"


class TransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


def inr_to_paise(amount: float) -> int:
    """Safely convert INR decimal to integer paise using Decimal."""
    d = Decimal(str(amount))
    return int((d * Decimal(100)).quantize(Decimal("1")))


def paise_to_inr(paise: int) -> float:
    """Safely convert integer paise back to INR float."""
    d = Decimal(paise) / Decimal(100)
    return float(d)


# --- Request Schemas ---

class CreateAccountRequest(BaseModel):
    holderName: str = Field(..., min_length=2, max_length=100, description="Full name of account holder")
    accountType: AccountType = Field(default=AccountType.SAVINGS, description="Type of account")
    ifsc: Optional[str] = Field(default="MOCK0001234", max_length=15, description="IFSC code")
    initialDeposit: float = Field(default=0.0, ge=0.0, description="Initial deposit in INR (default ₹0.0)")

    @field_validator("holderName")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("holderName must be at least 2 characters")
        return cleaned


class TransferRequest(BaseModel):
    fromAccountId: str = Field(..., min_length=3, description="Source account ID")
    toAccountId: str = Field(..., min_length=3, description="Destination account ID or external VPA")
    amount: float = Field(..., gt=0.0, description="Transfer amount in INR (must be positive)")
    mode: TransferMode = Field(default=TransferMode.INTERNAL, description="Transfer network/mode")
    referenceNote: Optional[str] = Field(default="Transfer", max_length=200, description="Reference remark")

    @field_validator("amount")
    @classmethod
    def check_min_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        # Ensure at least 1 paisa (₹0.01)
        if inr_to_paise(v) < 1:
            raise ValueError("Minimum transfer amount is ₹0.01")
        return v


class FreezeAccountRequest(BaseModel):
    reason: Optional[str] = Field(default="Security caution: Suspected scam or OTP leak", max_length=250)


# --- Response Schemas ---

class AccountResponse(BaseModel):
    accountId: str
    holderName: str
    accountType: AccountType
    ifsc: str
    balance: float = Field(..., description="Current balance in INR (e.g. ₹50000.50)")
    balancePaise: int = Field(..., description="Integer paise (avoiding float drift)")
    status: AccountStatus
    createdAt: str


class TransactionResponse(BaseModel):
    txnId: str
    fromAccountId: str
    toAccountId: str
    amount: float = Field(..., description="Transaction amount in INR")
    amountPaise: int = Field(..., description="Transaction amount in integer paise")
    currency: str = "INR"
    mode: TransferMode
    status: TransactionStatus
    referenceNote: Optional[str] = None
    timestamp: str


class StatementSummary(BaseModel):
    totalCreditsInr: float
    totalDebitsInr: float
    netFlowInr: float


class StatementResponse(BaseModel):
    accountId: str
    holderName: str
    currentBalance: float
    totalTransactions: int
    limit: int
    offset: int
    transactions: List[TransactionResponse]
    summary: StatementSummary


# --- Error Schemas ---

class ApiErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ApiErrorResponse(BaseModel):
    error: ApiErrorDetail
