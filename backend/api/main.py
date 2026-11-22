"""
SwaraGuard AI - FastAPI Backend
Main application with all API endpoints for scam detection and financial protection.
"""
import os
import shutil
import tempfile
import uuid
import json
import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models import (
    DeviceEvent, DeviceEventRequest, DeviceRiskResponse,
    FreezeAccountRequest, FreezeAccountResponse, GuardianAlert,
    GuardianDecisionRequest, GuardianDecisionResponse, RiskScoreRequest,
    RiskScoreResponse, ScamIntentResult, SensitiveInfoDetection,
    TransferRequest, TransferResponse, VoiceAnalysisResponse
)

from .state import DemoState, TransactionLock
from .risk_engine import risk_engine

# Import the enhanced audio analyzer
from .analyze_audio import audio_analyzer

# Try Gemini import
PLACEHOLDER_KEYS = {"your_key_here", "your_api_key_here", "your_key", "changeme", ""}
try:
    from dotenv import load_dotenv
    load_dotenv()
    from google import genai
    from google.genai import types
    _raw_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    HAS_GEMINI = bool(_raw_key) and _raw_key.lower() not in PLACEHOLDER_KEYS
    GEMINI_CLIENT = genai.Client(api_key=_raw_key) if HAS_GEMINI else None
except Exception:
    HAS_GEMINI = False
    GEMINI_CLIENT = None

# ==================== FastAPI App ====================

app = FastAPI(
    title="SwaraGuard AI - Scam Detection Backend",
    version="1.0.0",
    description="AI-powered scam call detection and financial protection system",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo state
demo_state = DemoState()

# ==================== Utility Functions ====================

def generate_event_id() -> str:
    return f"EVT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"


def add_audit_event(event_type: str, description: str, risk_score: float = None):
    demo_state.add_audit_event(event_type, description, risk_score)


# ==================== Voice Intelligence Endpoints ====================

@app.get("/")
async def root():
    return {
        "message": "SwaraGuard AI Backend",
        "status": "running",
        "version": "1.0.0",
        "gemini_configured": HAS_GEMINI,
        "endpoints": [
            "/api/analyze-audio",
            "/api/analyze-transcript",
            "/api/device-event",
            "/api/risk-score",
            "/api/freeze-account",
            "/api/transfer",
            "/api/guardian-decision",
            "/api/dashboard",
            "/api/demo-data",
            "/api/events",
            "/api/reset",
        ]
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "gemini_configured": HAS_GEMINI}


# Serve the colorful dashboard UI
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_ui():
    return FileResponse(os.path.join(DASHBOARD_DIR, "index.html"))


@app.get("/dashboard/style.css")
async def dashboard_css():
    return FileResponse(os.path.join(DASHBOARD_DIR, "style.css"))


@app.get("/dashboard/app.js")
async def dashboard_js():
    return FileResponse(os.path.join(DASHBOARD_DIR, "app.js"))


@app.get("/style.css")
async def root_css():
    return FileResponse(os.path.join(DASHBOARD_DIR, "style.css"))


@app.get("/app.js")
async def root_js():
    return FileResponse(os.path.join(DASHBOARD_DIR, "app.js"))


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return FileResponse(os.path.join(DASHBOARD_DIR, "login.html"))


@app.get("/live-call")
async def live_call_guard():
    return FileResponse(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "web-designs",
            "live_call_guard.html",
        )
    )


@app.get("/favicon.ico")
async def favicon():
    from fastapi import Response
    return Response(status_code=204)


@app.post("/api/login")
async def api_login():
    return RedirectResponse("/dashboard", status_code=302)


@app.post("/api/analyze-audio")
async def analyze_audio(
    file: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    session_id: str = Query(default=""),
    demo_scenario: Optional[str] = Query(default=None, alias="demo"),
    is_unknown_number: bool = Query(default=False),
):
    """
    Analyze an uploaded audio clip for scam / deepfake indicators.

    Returns the flat result shape the web UI renders:
    transcript, language_detected, risk_score, verdict,
    deepfake_voice_indicators, scam_tactics_detected,
    sensitive_info_leaked, leaked_items, user_advice.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    upload = file or audio

    try:
        if upload:
            suffix = os.path.splitext(upload.filename or "audio.wav")[1] or ".wav"
            if suffix not in [".wav", ".mp3", ".m4a", ".webm", ".ogg"]:
                suffix = ".wav"

            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="wb") as tmp:
                    shutil.copyfileobj(upload.file, tmp)
                    temp_path = tmp.name

                transcript_text = ""
                if HAS_GEMINI and GEMINI_CLIENT:
                    try:
                        response = GEMINI_CLIENT.models.generate_content(
                            model="gemini-1.5-flash",
                            contents=[temp_path, "Transcribe the audio content accurately. Return only the transcript."],
                        )
                        transcript_text = response.text
                    except Exception as e:
                        print(f"Gemini transcription failed: {e}")

                result = audio_analyzer.analyze_audio(
                    transcript_text=transcript_text,
                    is_unknown_number=is_unknown_number,
                )
                demo_state.current_risk_score = result.voice_risk_score
                add_audit_event("AUDIO_ANALYSIS", f"Analyzed audio: {upload.filename}", result.voice_risk_score)
                return {
                    "transcript": result.transcription.text,
                    "language_detected": result.transcription.language_detected,
                    "risk_score": result.voice_risk_score,
                    "verdict": (
                        "HIGH_RISK_SCAM" if result.voice_risk_score >= 80
                        else "SUSPICIOUS" if result.voice_risk_score >= 40
                        else "SAFE"
                    ),
                    "deepfake_voice_indicators": result.deepfake.indicators or ["None detected"],
                    "scam_tactics_detected": result.scam_intent.intent_categories or ["None"],
                    "sensitive_info_leaked": False,
                    "leaked_items": ["None"],
                    "user_advice": (
                        "Disconnect immediately and never share OTPs or PINs."
                        if result.voice_risk_score >= 40
                        else "No scam or synthetic voice indicators detected."
                    ),
                }
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

        # Demo scenario — map the internal shape to the flat UI shape.
        if demo_scenario:
            result = audio_analyzer.analyze_audio(
                demo_scenario=demo_scenario,
                is_unknown_number=is_unknown_number,
            )
            demo_state.current_risk_score = result.voice_risk_score
            add_audit_event("AUDIO_ANALYSIS", f"Demo scenario: {demo_scenario}", result.voice_risk_score)
            return {
                "transcript": result.transcription.text,
                "language_detected": result.transcription.language_detected,
                "risk_score": result.voice_risk_score,
                "verdict": (
                    "HIGH_RISK_SCAM" if result.voice_risk_score >= 80
                    else "SUSPICIOUS" if result.voice_risk_score >= 40
                    else "SAFE"
                ),
                "deepfake_voice_indicators": result.deepfake.indicators or ["None detected"],
                "scam_tactics_detected": result.scam_intent.intent_categories or ["None"],
                "sensitive_info_leaked": False,
                "leaked_items": ["None"],
                "user_advice": (
                    "Disconnect immediately and never share OTPs or PINs."
                    if result.voice_risk_score >= 40
                    else "No scam or synthetic voice indicators detected."
                ),
            }

        raise HTTPException(status_code=400, detail="No audio file or demo scenario provided")

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-transcript", response_model=VoiceAnalysisResponse)
async def analyze_transcript(
    transcript_text: str = "",
    session_id: str = Query(default=""),
    is_unknown_number: bool = Query(default=False)
):
    """Analyze raw transcript text without audio."""
    if not transcript_text:
        raise HTTPException(status_code=400, detail="Transcript text required")

    if not session_id:
        session_id = str(uuid.uuid4())

    result = audio_analyzer.analyze_transcript(transcript_text, is_unknown_number)
    demo_state.current_risk_score = result.voice_risk_score
    demo_state.current_risk_level = (
        "CRITICAL" if result.voice_risk_score >= 80 else
        "HIGH" if result.voice_risk_score >= 60 else
        "MEDIUM" if result.voice_risk_score >= 40 else
        "LOW"
    )
    add_audit_event("TRANSCRIPT_ANALYSIS", f"Analyzed transcript", result.voice_risk_score)
    return result


# ==================== Device Behaviour Endpoints ====================

@app.post("/api/device-event", response_model=DeviceRiskResponse)
async def analyze_device_event(request: DeviceEventRequest):
    """Analyze device events for suspicious activity."""
    if not request.session_id:
        request.session_id = str(uuid.uuid4())

    events_list = [
        {
            "event_type": e.event_type,
            "description": e.description,
            "risk_points": e.risk_points,
        }
        for e in request.events
    ]

    device_risk_score = risk_engine.calculate_device_risk(events_list)
    risk_factors = [e.description for e in request.events if e.risk_points > 10]
    suspicious_events = [e for e in request.events if e.risk_points > 10]

    response = DeviceRiskResponse(
        device_risk_score=device_risk_score,
        risk_factors=risk_factors,
        event_count=len(request.events),
        suspicious_events=[{"event_type": e.event_type, "description": e.description, "risk_points": e.risk_points} for e in suspicious_events],
        is_simulated=request.is_simulated,
    )

    demo_state.add_audit_event("DEVICE_EVENT", f"Device risk: {device_risk_score}", device_risk_score)
    return response


# ==================== Risk Engine Endpoint ====================

@app.post("/api/risk-score", response_model=RiskScoreResponse)
async def calculate_risk_score(request: RiskScoreRequest):
    """Calculate unified risk score from voice, device, and transaction data."""
    if not request.session_id:
        request.session_id = str(uuid.uuid4())

    result = risk_engine.combine_risk_scores(
        request.voice_risk_score,
        request.device_risk_score,
        request.transaction_risk,
    )

    signals = risk_engine.build_signals(
        request.voice_risk_score,
        request.device_risk_score,
        request.transaction_risk,
        request.voice_signals,
        request.device_signals,
        request.transaction_signals,
    )

    response = RiskScoreResponse(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        signals=signals,
        recommended_action=result["recommended_action"],
        voice_risk=request.voice_risk_score,
        device_risk=request.device_risk_score,
        transaction_risk=request.transaction_risk,
        is_simulated=request.is_simulated,
    )

    demo_state.current_risk_score = response.risk_score
    demo_state.current_risk_level = response.risk_level
    demo_state.add_audit_event("RISK_CALCULATION", f"Risk: {result['risk_level']} ({result['risk_score']})", result["risk_score"])

    return response


# ==================== Bank Service Endpoints ====================

@app.get("/api/account")
async def get_account():
    """Get current bank account info."""
    return {
        "name": demo_state.account["name"],
        "account_number": demo_state.account["account_number"],
        "balance": demo_state.account["balance"],
        "status": demo_state.account["status"],
        "currency": demo_state.account["currency"],
    }


@app.post("/api/freeze-account", response_model=FreezeAccountResponse)
async def freeze_account(request: FreezeAccountRequest):
    """Simulate freezing bank account for protection."""
    demo_state.account["status"] = "FROZEN"

    lock = TransactionLock(
        account_alias=request.account_alias,
        reason=request.reason,
        duration_minutes=request.duration_minutes,
    )
    demo_state.active_lock = lock
    demo_state.add_audit_event("ACCOUNT_FREEZE", f"Frozen: {request.reason}", 100.0)

    locked_until_utc = lock.locked_until

    return FreezeAccountResponse(
        status="SIMULATED_FREEZE_ACTIVE",
        disclaimer="Demo simulation only — third-party apps cannot directly freeze live bank accounts.",
        account_alias=request.account_alias,
        reason=request.reason,
        freeze_duration_minutes=request.duration_minutes,
        locked_until_utc=locked_until_utc,
        helpline_1930="1930",
        next_steps=[
            "Open your official bank or UPI app immediately and lock your debit/credit card.",
            "Change your UPI PIN, net-banking password, and MPIN right away.",
            "Call 1930 or visit cybercrime.gov.in if money was debited.",
        ],
        is_simulated=True,
    )


@app.post("/api/transfer", response_model=TransferResponse)
async def transfer(request: TransferRequest):
    """Process a bank transfer (simulated)."""
    if demo_state.account["status"] != "ACTIVE":
        return TransferResponse(
            success=False,
            message="Account is frozen - outgoing transactions blocked",
            status="REJECTED",
            is_simulated=True,
        )

    if request.amount > demo_state.account["balance"]:
        return TransferResponse(
            success=False,
            message="Insufficient funds",
            status="REJECTED",
            is_simulated=True,
        )

    demo_state.account["balance"] -= request.amount
    demo_state.add_audit_event("TRANSFER", f"Transfer: ₹{request.amount} to {request.to_beneficiary}", 0.0)

    return TransferResponse(
        success=True,
        transaction_id=f"TXN-{uuid.uuid4().hex[:8]}",
        message="Transfer processed successfully",
        status="SUCCESS",
        balance=demo_state.account["balance"],
        is_simulated=True,
    )


@app.post("/api/guardian-decision", response_model=GuardianDecisionResponse)
async def guardian_decision(request: GuardianDecisionRequest):
    """Guardian makes decision on account status."""
    if request.decision == "APPROVE_UNFREEZE":
        demo_state.account["status"] = "ACTIVE"
        demo_state.active_lock = None
        return GuardianDecisionResponse(
            decision=request.decision,
            account_status="ACTIVE",
            message="Guardian approved unfreezing account",
            is_simulated=True,
        )
    elif request.decision == "KEEP_FROZEN":
        demo_state.account["status"] = "FROZEN"
        return GuardianDecisionResponse(
            decision=request.decision,
            account_status="FROZEN",
            message="Guardian decided to keep account frozen",
            is_simulated=True,
        )

    return GuardianDecisionResponse(
        decision=request.decision,
        account_status=demo_state.account["status"],
        message="Decision recorded",
        is_simulated=True,
    )


@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard data for web frontend."""
    return {
        "account_status": demo_state.account["status"],
        "account_balance": demo_state.account["balance"],
        "risk_score": demo_state.current_risk_score,
        "risk_level": demo_state.current_risk_level,
        "active_lock": demo_state.active_lock is not None,
        "active_lock_minutes": demo_state.active_lock.duration_minutes if demo_state.active_lock else None,
        "lock_expires_at": demo_state.active_lock.locked_until.isoformat() if demo_state.active_lock else None,
        "guardian_alerts": len(demo_state.guardian_alerts),
        "total_audit_events": len(demo_state.audit_log),
        "is_simulated": True,
    }


@app.get("/api/events")
async def get_events():
    """Get audit log events."""
    return {"events": demo_state.audit_log}


# ==================== Guardian Endpoints ====================

@app.post("/api/guardian-alert")
async def guardian_alert(risk_level: str, risk_score: float, reasons: str):
    """Send alert to guardian."""
    alert = GuardianAlert(
        alert_id=f"ALERT-{uuid.uuid4().hex[:8]}",
        risk_level=risk_level,
        risk_score=risk_score,
        detected_reasons=[r.strip() for r in reasons.split(",") if r.strip()],
        recommended_action=(
            "PROTECT_ACCOUNT" if risk_score >= 80 else
            "WARN_USER" if risk_score >= 60 else
            "MONITOR"
        ),
        is_simulated=True,
    )
    demo_state.guardian_alerts.append(alert.dict())
    demo_state.add_audit_event("GUARDIAN_ALERT", f"Guardian alert: {risk_level}", risk_score)
    return alert


# ==================== Sensitive Info Endpoint ====================

@app.post("/api/sensitive-info", response_model=SensitiveInfoDetection)
async def detect_sensitive_info(transcript: str = ""):
    """Detect sensitive information in transcript without storing values."""
    detected = False
    detail_type = None
    risk_level = "LOW"

    otp_pattern = re.compile(r'\b\d{4,6}\b')
    cvv_pattern = re.compile(r'\bcvv\b', re.IGNORECASE)
    pin_pattern = re.compile(r'\bpin\b', re.IGNORECASE)

    if otp_pattern.search(transcript):
        detected = True
        detail_type = "OTP"
        risk_level = "HIGH"

    if cvv_pattern.search(transcript):
        detected = True
        detail_type = "CVV"
        risk_level = "CRITICAL"

    if pin_pattern.search(transcript):
        detected = True
        detail_type = "PIN"
        risk_level = "HIGH"

    return SensitiveInfoDetection(
        sensitive_detail_detected=detected,
        detail_type=detail_type,
        actual_value=None,  # Never store actual values
        risk_level=risk_level,
        context="Call analysis",
    )


# ==================== Reset Endpoint ====================

@app.post("/api/reset", response_model=Dict)
async def reset():
    """Reset all demo state."""
    demo_state.reset()
    return {"status": "RESET", "message": "All demo state has been reset", "is_simulated": True}


# ==================== Demo Data Endpoint ====================

@app.get("/api/demo-data")
async def get_demo_data():
    """Get pre-configured demo scenarios for presentation."""
    return {
        "scenarios": [
            {
                "name": "bank_scam",
                "title": "AI-Generated Bank Scam",
                "description": "Fake bank rep requests OTP for KYC verification",
                "expected_risk": "CRITICAL",
                "transcript": "Hello sir, this is calling from HDFC Bank. Your KYC is expiring today. If you don't verify immediately your account will be blocked. Please share the OTP I just sent to your phone number to complete verification. This is urgent, you must act now."
            },
            {
                "name": "digital_arrest",
                "title": "Digital Arrest Scam",
                "description": "Fake police officer threatens arrest, requests remote access",
                "expected_risk": "CRITICAL",
            },
            {
                "name": "family_safe",
                "title": "Family Call (Safe Scenario)",
                "description": "Unknown number but normal, non-coercive conversation",
                "expected_risk": "LOW",
            },
            {
                "name": "telugu_scam",
                "title": "Telugu Regional Scam",
                "description": "Scam in telugu language targeting regional users",
                "expected_risk": "HIGH",
            },
            {
                "name": "hinglish_scam",
                "title": "Hinglish Scam",
                "description": "Mixed Hindi-English scam targeting urban users",
                "expected_risk": "HIGH",
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
