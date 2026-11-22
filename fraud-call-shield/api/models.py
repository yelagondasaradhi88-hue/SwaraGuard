"""
Pydantic data models for Fraud Call Shield API.
All models use explicit typing and docstrings for clean student presentations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeviceEventRequest(BaseModel):
    """Payload representing a device telemetric signal or user action."""
    event_type: str = Field(..., description="Unique event identifier (e.g. unknown_call_active, apk_sideloaded)")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata like url, app_name, etc.")
    timestamp: Optional[datetime] = Field(default=None, description="ISO timestamp of when event occurred")


class DeviceEventResponse(BaseModel):
    """Response returned after processing a device event and re-evaluating risk."""
    score: int = Field(..., description="Risk score 0-100")
    tier: str = Field(..., description="NORMAL, WARN, SOFT_PROTECT, or FREEZE")
    reasons: List[str] = Field(default_factory=list, description="Human-readable explanations of risk factors")
    action_taken: str = Field(..., description="Description of automated action executed")
    processing_ms: float = Field(..., description="Latency of risk calculation in milliseconds")


class TransferRequest(BaseModel):
    """Request to transfer funds to a payee."""
    to_account: str = Field(..., description="Payee account identifier")
    amount: float = Field(..., gt=0, description="Amount to transfer")


class TransferResponse(BaseModel):
    """Decision returned by mock bank for fund transfer request."""
    decision: str = Field(..., description="ALLOW, STEP_UP, or HOLD")
    score: int = Field(..., description="Evaluated risk score at time of transfer")
    reasons: List[str] = Field(default_factory=list, description="Reasons contributing to decision")
    processing_ms: float = Field(..., description="Latency of bank decision in milliseconds")
    message: str = Field(..., description="User-facing message")
    verification_required: bool = Field(default=False, description="True if step-up verification is needed")
    security_question: Optional[str] = Field(default=None, description="Security question when STEP_UP is triggered")


class VerifyTransferRequest(BaseModel):
    """Verification step-up response for SOFT_PROTECT tier."""
    answer: str = Field(..., description="Answer to the step-up security question")


class VerifyAndUnfreezeRequest(BaseModel):
    """Answers submitted during bank callback to unfreeze account."""
    q1_answer: str = Field(..., description="Answer to Security Question 1")
    q2_answer: str = Field(..., description="Answer to Security Question 2")


class GuardianDecisionRequest(BaseModel):
    """Family guardian approval or rejection of safety hold."""
    approve: bool = Field(..., description="True to release hold and restore ACTIVE status, False to keep frozen")


class AccountStateResponse(BaseModel):
    """Full snapshot of the mock bank account state."""
    name: str
    account_no: str
    balance: float
    status: str
    frozen_until: Optional[str] = None
    callback_pending: bool
    protected_user: bool
    typical_max_transfer: float
    known_payees: List[str]
    guardian: Dict[str, str]
    tier: str
    current_score: int
