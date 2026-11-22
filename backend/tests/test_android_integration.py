"""
Android integration tests for SwaraGuard.
"""
import pytest
from backend.risk_engine import analyze_audio_result


def test_full_workflow_simulation():
    """Simulate the complete workflow from audio to risk score."""
    # Mock audio result with high-risk indicators
    mock_result = {
        "transcript": "Please share your OTP 123456 immediately or your account will be blocked. Act now!",
        "language_detected": "en",
        "deepfake_voice_indicators": ["Robotic/flat voice", "Unnaturally uniform pitch"],
        "scam_tactics_detected": ["OTP request", "Urgent money transfer"],
        "sensitive_info_leaked": True,
        "leaked_items": ["otp"],
        "user_advice": "🚨 HIGH RISK: Immediately stop call, do NOT share any information, and initiate protection flow.",
        "should_initiate_protection": True,
    }

    result = analyze_audio_result(mock_result)

    # Verify all components are present
    assert result["transcript"] is not None
    assert result["language_detected"] == "en"
    assert len(result["deepfake_voice_indicators"]) > 0
    assert len(result["scam_tactics_detected"]) > 0
    assert result["sensitive_info_leaked"] is True
    assert result["leaked_items"] == ["otp"]
    assert result["should_initiate_protection"] is True

    # Verify risk scoring components
    assert result["risk_score"] >= 60
    assert result["verdict"] in ["HIGH_RISK_SCAM", "SUSPICIOUS"]
    assert result["risk_level"] in ["CRITICAL", "HIGH", "MEDIUM", "Medium", "High"]
    assert result["user_advice"] is not None