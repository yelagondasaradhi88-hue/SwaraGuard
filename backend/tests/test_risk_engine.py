"""
Tests for the risk engine.
"""
import pytest
from backend.api.risk_engine import risk_engine, RiskEngine


def test_low_risk_no_scam():
    result = risk_engine.combine_risk_scores(0, 0, 0)
    assert result["risk_score"] == 0
    assert result["risk_level"] == "LOW"
    assert result["recommended_action"] == "MONITOR"


def test_high_risk_combined():
    result = risk_engine.combine_risk_scores(89, 75, 60)
    assert result["risk_score"] == 77.6
    assert result["risk_level"] == "HIGH"
    assert result["recommended_action"] == "WARN_AND_PROTECT"


def test_critical_risk_combined():
    result = risk_engine.combine_risk_scores(90, 85, 80)
    assert result["risk_level"] == "CRITICAL"
    assert result["recommended_action"] == "PROTECT_ACCOUNT"


def test_device_risk_calculation():
    events = [
        {"event_type": "SCREEN_SHARE", "risk_points": 40},
        {"event_type": "ACCESSIBILITY", "risk_points": 35},
    ]
    score = risk_engine.calculate_device_risk(events)
    assert score == 75.0


def test_transaction_risk_locked():
    score = risk_engine.calculate_transaction_risk(locked=True, transaction_count=5, amount=15000)
    assert score == 65.0


def test_voice_risk_calculation():
    score = risk_engine.calculate_voice_risk(voice_risk_score=0, deepfake_prob=0.85, scam_tactics_count=3)
    assert score >= 40