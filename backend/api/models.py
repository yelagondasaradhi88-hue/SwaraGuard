"""
SwaraGuard AI - Pydantic Models
Defines all request and response schemas for the FastAPI backend.
Production-ready with proper validation and documentation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Voice Intelligence Models ====================

class TranscriptionResult(BaseModel):
    """Speech-to-text transcription result."""
    text: str = ""
    language_detected: str = "en"
    confidence: float = 0.0
    suspicious_phrases: list = []
    is_mock: bool = True


class DeepfakeDetectionResult(BaseModel):
    """Deepfake voice detection result."""
    synthetic_probability: float = 0.0
    is_suspicious: bool = False
    model: str = "MockDeepfakeDetector"
    indicators: list = []
    is_mock: bool = True


class ScamIntentResult(BaseModel):
    """Scam intent classification result."""
    scam_detected: bool = False
    intent_categories: list = []
    confidence: float = 0.0
    reasons: list = []
    is_mock: bool = True


class CallerTypeAssessment(str, Enum):
    UNKNOWN = "unknown"
    FAMILIAR = "familiar"
    OFFICIAL = "official"
    SUSPECTED_SCAMMER = "suspected_scammer"


class Verdict(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK_SCAM = "HIGH_RISK_SCAM"


class AutoDisconnectRecommended(str, Enum):
    YES = "true"
    NO = "false"


class VoiceAnalysisResponse(BaseModel):
    """Complete voice analysis response."""
    transcription: TranscriptionResult = Field(default_factory=TranscriptionResult)
    deepfake: DeepfakeDetectionResult = Field(default_factory=DeepfakeDetectionResult)
    scam_intent: ScamIntentResult = Field(default_factory=ScamIntentResult)
    voice_risk_score: float = 0.0
    risk_level: str = "LOW"
    verdict: str = "SAFE"
    auto_disconnect_recommended: str = "false"
    user_advice: str = "Continue normal conversation"
    processing_time_ms: float = 0.0
    is_mock: bool = True


# ==================== Device Behaviour Models ====================

class DeviceEvent(BaseModel):
    """Single device event for analysis."""
    event_type: str
    description: str = ""
    timestamp: Optional[datetime] = None
    risk_points: int = 0
    metadata: Dict[str, Any] = {}
    is_simulated: bool = True


class DeviceEventRequest(BaseModel):
    """Request to submit device events."""
    session_id: str = ""
    events: List[DeviceEvent] = []
    is_simulated: bool = True


class DeviceRiskResponse(BaseModel):
    """Device risk analysis response."""
    device_risk_score: float = 0.0
    risk_factors: List[str] = []
    event_count: int = 0
    suspicious_events: List[Dict[str, Any]] = []
    is_simulated: bool = True


# ==================== Unified Risk Engine Models ====================

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendedAction(str, Enum):
    MONITOR = "MONITOR"
    WARN_USER = "WARN_USER"
    PROTECT_ACCOUNT = "PROTECT_ACCOUNT"


class RiskScoreRequest(BaseModel):
    """Request to calculate unified risk score."""
    session_id: str = ""
    voice_risk_score: float = 0.0
    device_risk_score: float = 0.0
    transaction_risk: float = 0.0
    voice_signals: List[str] = []
    device_signals: List[str] = []
    transaction_signals: List[str] = []
    is_simulated: bool = True


class RiskScoreResponse(BaseModel):
    """Unified risk score response."""
    risk_score: float = 0.0
    risk_level: str = "LOW"
    signals: List[str] = []
    recommended_action: str = "MONITOR"
    voice_risk: float = 0.0
    device_risk: float = 0.0
    transaction_risk: float = 0.0
    is_simulated: bool = True


# ==================== Sensitive Information Models ====================

class SensitiveInfoDetection(BaseModel):
    """Sensitive information detection result."""
    sensitive_detail_detected: bool = False
    detail_type: Optional[str] = None
    actual_value: Optional[str] = None  # Always null - never store
    risk_level: str = "LOW"
    context: str = ""


# ==================== Bank Models ====================

class AccountInfo(BaseModel):
    """Fake bank account information."""
    name: str = "Demo User"
    account_number: str = "XXXX1234"
    balance: float = 50000.0
    status: str = "ACTIVE"
    currency: str = "INR"


class Beneficiary(BaseModel):
    """Fake beneficiary information."""
    id: str
    name: str
    account: str
    is_known: bool = True


class FreezeAccountRequest(BaseModel):
    """Request to freeze account."""
    account_alias: str = "XXXX1234"
    reason: str = "High-risk scam detected"
    duration_minutes: int = 900  # 15 minutes (simulated protection)
    trigger_event: str = "risk_engine"
    is_simulated: bool = True


class FreezeAccountResponse(BaseModel):
    """Freeze account response."""
    status: str = "SIMULATED_FREEZE_ACTIVE"
    disclaimer: str = "Demo simulation only — third-party apps cannot directly freeze live bank accounts."
    account_alias: str = ""
    reason: str = ""
    freeze_duration_minutes: int = 900
    locked_until_utc: Optional[datetime] = None
    helpline_1930: str = "1930"
    next_steps: List[str] = []
    is_simulated: bool = True


class TransferRequest(BaseModel):
    """Transfer request."""
    from_account: str = "XXXX1234"
    to_beneficiary: str = ""
    amount: float = 0.0
    description: str = ""
    is_simulated: bool = True


class TransferResponse(BaseModel):
    """Transfer response."""
    success: bool = False
    transaction_id: Optional[str] = None
    message: str = ""
    balance: Optional[float] = None
    status: str = "REJECTED"
    is_simulated: bool = True


class VerifyTransferRequest(BaseModel):
    """Additional verification request."""
    transaction_id: str
    otp: str = ""
    security_question: str = ""
    is_simulated: bool = True


class VerifyTransferResponse(BaseModel):
    """Verification response."""
    verified: bool = False
    message: str = ""
    is_simulated: bool = True


# ==================== Guardian Models ====================

class GuardianAlert(BaseModel):
    """Guardian alert notification."""
    alert_id: str
    user_id: str = "demo_user"
    risk_level: str = "LOW"
    risk_score: float = 0.0
    detected_reasons: List[str] = []
    recommended_action: str = "MONITOR"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_simulated: bool = True


class GuardianDecisionRequest(BaseModel):
    """Guardian decision on account status."""
    decision: str  # APPROVE_UNFREEZE, KEEP_FROZEN
    guardian_note: str = ""
    is_simulated: bool = True


class GuardianDecisionResponse(BaseModel):
    """Guardian decision response."""
    decision: str
    account_status: str
    message: str
    is_simulated: bool = True


# ==================== Bank Callback Models ====================

class BankCallbackResponse(BaseModel):
    """Simulated bank callback message."""
    message: str
    verification_required: bool = True
    next_steps: List[str] = []
    is_simulated: bool = True


class VerifyAndUnfreezeRequest(BaseModel):
    """Request to verify and unfreeze account."""
    verification_method: str = "otp"
    verification_value: str = ""
    is_simulated: bool = True


class VerifyAndUnfreezeResponse(BaseModel):
    """Verify and unfreeze response."""
    success: bool = False
    account_status: str = "FROZEN"
    message: str = ""
    is_simulated: bool = True


# ==================== Audit Log Models ====================

class AuditEvent(BaseModel):
    """Audit log event."""
    id: str
    timestamp: datetime
    event_type: str
    description: str
    risk_score: Optional[float] = None
    is_simulated: bool = True


# ==================== Reset Model ====================

class ResetResponse(BaseModel):
    """Reset response."""
    status: str = "RESET"
    message: str = "All demo state has been reset"
    is_simulated: bool = True