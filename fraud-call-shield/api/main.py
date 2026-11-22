"""
FastAPI application for Fraud Call Shield mock bank server.
Provides endpoints for device telemetry ingestion, transfer fraud gating,
guardian authorization, and simulated bank callback verification.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from api.models import (
    DeviceEventRequest,
    DeviceEventResponse,
    TransferRequest,
    TransferResponse,
    VerifyTransferRequest,
    VerifyAndUnfreezeRequest,
    GuardianDecisionRequest,
    AccountStateResponse
)
from api.risk_engine import evaluate_risk
from api.state import bank_state

app = FastAPI(
    title="Fraud Call Shield - Mock Bank API",
    description="Proactive fraud prevention gateway detecting scam chains and freezing outgoing transfers before money leaves.",
    version="1.0.0"
)

# Enable CORS for Streamlit / external UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/device-event", response_model=DeviceEventResponse)
def post_device_event(payload: DeviceEventRequest):
    """
    Ingests a device telemetry event (e.g. unknown call, APK sideload, screen share).
    Recomputes threat score in the 15-minute sliding window, determines tier,
    and executes automated defensive actions within milliseconds.
    """
    start_time = time.perf_counter()

    # 1. Check auto-unfreeze if freeze window expired
    bank_state.check_auto_unfreeze()

    # 2. Ingest the event into the sliding window
    event_dict = {
        "event_type": payload.event_type,
        "details": payload.details or {},
        "timestamp": payload.timestamp.isoformat() if payload.timestamp else datetime.now(timezone.utc).isoformat()
    }
    bank_state.add_event(event_dict)

    # 3. Evaluate risk using pure engine
    evaluation = evaluate_risk(
        events=bank_state.session_events,
        protected_user=bank_state.account["protected_user"],
        typical_max_transfer=bank_state.account["typical_max_transfer"]
    )

    score = evaluation["score"]
    tier = evaluation["tier"]
    reasons = evaluation["reasons"]

    # 4. Enforce Tier Policy
    action_taken = "Baseline monitoring; normal telemetry recorded."
    if tier == "WARN":
        action_taken = "In-app warning triggered: 'Banks never ask you to install apps or share your screen.'"
        bank_state.log_audit("WARN_BANNER_SHOWN", action_taken)

    elif tier == "SOFT_PROTECT":
        action_taken = "Step-up verification enforced on transfers; Guardian notified."
        bank_state.notify_guardian("WARNING", "Suspicious device activity pattern detected.", reasons)

    elif tier == "FREEZE":
        if bank_state.account["status"] != "FROZEN":
            bank_state.freeze_account(duration_minutes=30, reasons=reasons)
            action_taken = "CRITICAL: Outgoing transfers FROZEN for 30 minutes; Guardian alerted; Bank callback queued."
        else:
            action_taken = "Threat sustained; Outgoing transfers remain FROZEN."

    processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
    bank_state.last_decision_ms = processing_ms

    return DeviceEventResponse(
        score=score,
        tier=tier,
        reasons=reasons,
        action_taken=action_taken,
        processing_ms=processing_ms
    )


@app.post("/transfer", response_model=TransferResponse)
def post_transfer(payload: TransferRequest):
    """
    Evaluates fund transfer attempt against device telemetry risk context.
    - If account is FROZEN: Immediately holds transaction.
    - Automatically adds new_payee (+15) and large_amount (+20) if applicable.
    - If score hits FREEZE threshold (70+): Freezes account and holds money.
    - If SOFT_PROTECT (50-69): Demands step-up security verification.
    - Otherwise: Allows transfer and debits balance.
    """
    start_time = time.perf_counter()
    bank_state.check_auto_unfreeze()

    # 1. Existing Freeze Check
    if bank_state.account["status"] == "FROZEN":
        processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
        evaluation = evaluate_risk(
            events=bank_state.session_events,
            protected_user=bank_state.account["protected_user"],
            typical_max_transfer=bank_state.account["typical_max_transfer"]
        )
        return TransferResponse(
            decision="HOLD",
            score=evaluation["score"],
            reasons=["Account outgoing transfers are temporarily FROZEN for your protection."] + evaluation["reasons"],
            processing_ms=processing_ms,
            message="Payment paused for your safety. Your bank will call you to verify.",
            verification_required=False
        )

    # 2. Check for payment-specific risk events and inject into session window
    is_new_payee = payload.to_account not in bank_state.account["known_payees"]
    is_large_amount = payload.amount > (3 * bank_state.account["typical_max_transfer"])

    if is_new_payee:
        bank_state.add_event({
            "event_type": "new_payee",
            "details": {"to_account": payload.to_account},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    if is_large_amount:
        bank_state.add_event({
            "event_type": "large_amount",
            "details": {
                "amount": payload.amount,
                "typical_max": bank_state.account["typical_max_transfer"],
                "multiplier": payload.amount / bank_state.account["typical_max_transfer"]
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # 3. Re-evaluate risk with payment telemetry incorporated
    evaluation = evaluate_risk(
        events=bank_state.session_events,
        protected_user=bank_state.account["protected_user"],
        typical_max_transfer=bank_state.account["typical_max_transfer"]
    )
    score = evaluation["score"]
    tier = evaluation["tier"]
    reasons = evaluation["reasons"]

    # 4. Check if score crossed FREEZE threshold (70+)
    if tier == "FREEZE":
        bank_state.freeze_account(duration_minutes=30, reasons=reasons)
        processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
        bank_state.log_audit("TRANSFER_BLOCKED_FREEZE", {
            "to_account": payload.to_account,
            "amount": payload.amount,
            "score": score
        })
        return TransferResponse(
            decision="HOLD",
            score=score,
            reasons=reasons,
            processing_ms=processing_ms,
            message="Payment paused for your safety. Your bank will call you to verify.",
            verification_required=False
        )

    # 5. Check if SOFT_PROTECT applies (50-69)
    if tier == "SOFT_PROTECT":
        # Stash pending transfer for step-up verification
        bank_state.pending_transfer = {
            "to_account": payload.to_account,
            "amount": payload.amount,
            "required_question_id": "q1",
            "expected_answer": bank_state.account["security_questions"][0]["answer"]
        }
        question = bank_state.account["security_questions"][0]["question"]
        processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
        bank_state.log_audit("TRANSFER_STEP_UP_REQUIRED", {
            "to_account": payload.to_account,
            "amount": payload.amount,
            "score": score
        })
        return TransferResponse(
            decision="STEP_UP",
            score=score,
            reasons=reasons,
            processing_ms=processing_ms,
            message="Verification required: Please answer your security question to complete this transfer.",
            verification_required=True,
            security_question=question
        )

    # 6. Check balance sufficiency
    if bank_state.account["balance"] < payload.amount:
        processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: INR {bank_state.account['balance']:,.2f}"
        )

    # 7. Execute ALLOW
    bank_state.account["balance"] -= payload.amount
    processing_ms = round((time.perf_counter() - start_time) * 1000, 2)
    bank_state.log_audit("TRANSFER_COMPLETED", {
        "to_account": payload.to_account,
        "amount": payload.amount,
        "new_balance": bank_state.account["balance"],
        "score": score
    })

    return TransferResponse(
        decision="ALLOW",
        score=score,
        reasons=reasons,
        processing_ms=processing_ms,
        message=f"Transfer of INR {payload.amount:,.2f} to {payload.to_account} completed successfully.",
        verification_required=False
    )


@app.post("/verify-transfer")
def verify_transfer(request: Request, payload: Optional[Dict[str, Any]] = None):
    """
    Submits step-up security verification for a pending SOFT_PROTECT transfer.
    Moves money only upon successful verification.
    """
    if not bank_state.pending_transfer:
        raise HTTPException(status_code=400, detail="No pending transfer found requiring verification.")

    # Accommodate flexible body payload formats
    answer = ""
    if payload:
        answer = payload.get("answer") or payload.get("answers", {}).get("answer", "")
    
    expected = bank_state.pending_transfer["expected_answer"]
    if not answer or answer.strip().lower() != expected.lower():
        bank_state.log_audit("STEP_UP_FAILED", {"given_answer": answer})
        raise HTTPException(status_code=403, detail="Incorrect security answer. Transfer not approved.")

    # Successful verification -> execute transfer
    to_account = bank_state.pending_transfer["to_account"]
    amount = bank_state.pending_transfer["amount"]

    if bank_state.account["balance"] < amount:
        bank_state.pending_transfer = None
        raise HTTPException(status_code=400, detail="Insufficient funds.")

    bank_state.account["balance"] -= amount
    bank_state.pending_transfer = None
    bank_state.log_audit("TRANSFER_COMPLETED_AFTER_STEP_UP", {
        "to_account": to_account,
        "amount": amount,
        "new_balance": bank_state.account["balance"]
    })

    return {
        "success": True,
        "decision": "ALLOW",
        "message": f"Step-up verified! Transfer of INR {amount:,.2f} to {to_account} completed successfully.",
        "remaining_balance": bank_state.account["balance"]
    }


@app.get("/account", response_model=AccountStateResponse)
def get_account():
    """Returns current mock bank account status, balance, and risk tier."""
    bank_state.check_auto_unfreeze()
    evaluation = evaluate_risk(
        events=bank_state.session_events,
        protected_user=bank_state.account["protected_user"],
        typical_max_transfer=bank_state.account["typical_max_transfer"]
    )
    return AccountStateResponse(
        name=bank_state.account["name"],
        account_no=bank_state.account["account_no"],
        balance=bank_state.account["balance"],
        status=bank_state.account["status"],
        frozen_until=bank_state.account["frozen_until"],
        callback_pending=bank_state.account["callback_pending"],
        protected_user=bank_state.account["protected_user"],
        typical_max_transfer=bank_state.account["typical_max_transfer"],
        known_payees=bank_state.account["known_payees"],
        guardian=bank_state.account["guardian"],
        tier=evaluation["tier"],
        current_score=evaluation["score"]
    )


@app.get("/events")
def get_events():
    """Returns the chronological audit log and active device event window."""
    bank_state.check_auto_unfreeze()
    evaluation = evaluate_risk(
        events=bank_state.session_events,
        protected_user=bank_state.account["protected_user"],
        typical_max_transfer=bank_state.account["typical_max_transfer"]
    )
    return {
        "sliding_window_events": bank_state.session_events,
        "audit_log": list(reversed(bank_state.audit_log)),
        "guardian_notifications": list(reversed(bank_state.guardian_notifications)),
        "current_evaluation": evaluation,
        "last_decision_ms": bank_state.last_decision_ms
    }


@app.get("/bank-callback")
def get_bank_callback():
    """
    Simulates inbound customer verification call from bank fraud department.
    Returns the operator conversation script and identity verification questions.
    """
    bank_state.check_auto_unfreeze()
    return {
        "status": bank_state.account["status"],
        "callback_pending": bank_state.account["callback_pending"],
        "caller_id": "YourBank Fraud Safety Desk (1800-SAFE-BANK)",
        "script": (
            "Hello Demo User, this is the Fraud Prevention Team from YourBank. "
            "We noticed abnormal telemetric activity on your mobile device (such as remote access "
            "or screen sharing during an unknown call) and placed a proactive hold on outgoing transfers "
            "to prevent unauthorized loss. To unfreeze your account and restore service, please verify your identity."
        ),
        "security_questions": [
            {"id": "q1", "question": bank_state.account["security_questions"][0]["question"]},
            {"id": "q2", "question": bank_state.account["security_questions"][1]["question"]}
        ],
        "guardian_notified": bank_state.account["guardian"]["name"]
    }


@app.post("/verify-and-unfreeze")
def verify_and_unfreeze(request: Request, payload: Optional[Dict[str, Any]] = None):
    """
    Validates answers to security questions during bank callback.
    Upon correct answers, clears threat window and restores account to ACTIVE.
    """
    if payload is None:
        payload = {}
    
    # Support both flat keys and nested answers dictionary
    answers = payload.get("answers", payload)
    q1_ans = answers.get("q1_answer") or answers.get("q1") or ""
    q2_ans = answers.get("q2_answer") or answers.get("q2") or ""

    expected_q1 = bank_state.account["security_questions"][0]["answer"]
    expected_q2 = bank_state.account["security_questions"][1]["answer"]

    q1_ok = q1_ans.strip().lower() == expected_q1.lower()
    q2_ok = q2_ans.strip().lower() == expected_q2.lower()

    if q1_ok and q2_ok:
        bank_state.unfreeze_account(actor="BANK_CALLBACK_VERIFIED")
        return {
            "success": True,
            "status": "ACTIVE",
            "message": "Identity successfully confirmed! Account outgoing transfers restored to ACTIVE."
        }
    else:
        bank_state.log_audit("UNFREEZE_ATTEMPT_FAILED", {
            "q1_correct": q1_ok,
            "q2_correct": q2_ok
        })
        raise HTTPException(
            status_code=400,
            detail="Verification failed. Answers did not match customer security profile. Account remains FROZEN for protection."
        )


@app.post("/guardian-decision")
def guardian_decision(payload: GuardianDecisionRequest):
    """
    Allows designated family guardian to review and release or maintain the fraud hold.
    """
    if payload.approve:
        bank_state.unfreeze_account(actor="GUARDIAN_APPROVAL")
        return {
            "success": True,
            "status": "ACTIVE",
            "message": "Guardian approved release. Account restored to ACTIVE status."
        }
    else:
        bank_state.log_audit("GUARDIAN_CONFIRMED_HOLD", "Family guardian instructed to maintain protective account freeze.")
        return {
            "success": True,
            "status": "FROZEN",
            "message": "Protective hold maintained as requested by family guardian."
        }


@app.post("/reset")
def reset_demo():
    """Resets the mock bank state, event history, and audit log to initial conditions."""
    bank_state.reset()
    return {
        "success": True,
        "message": "Demo state successfully reset to initial baseline."
    }
