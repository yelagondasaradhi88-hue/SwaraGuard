"""
Tests for audio analyzer demo scenarios.
"""
import pytest
from backend.api.audio_analyzer import audio_analyzer


def risk_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def test_bank_scam_scenario():
    result = audio_analyzer.analyze_audio(demo_scenario="bank_scam")
    assert result.voice_risk_score >= 80
    assert risk_level(result.voice_risk_score) == "CRITICAL"
    assert result.deepfake.is_suspicious is True
    assert result.scam_intent.scam_detected is True


def test_digital_arrest_scenario():
    result = audio_analyzer.analyze_audio(demo_scenario="digital_arrest")
    assert result.voice_risk_score >= 80
    assert risk_level(result.voice_risk_score) == "CRITICAL"
    assert result.deepfake.is_suspicious is True
    assert result.scam_intent.scam_detected is True


def test_normal_conversation():
    result = audio_analyzer.analyze_audio(demo_scenario="normal")
    assert risk_level(result.voice_risk_score) == "MEDIUM"
    assert result.deepfake.is_suspicious is True


def test_no_scenario():
    result = audio_analyzer.analyze_audio(demo_scenario=None)
    assert result.voice_risk_score == 4.0  # deepfake 0.1 * 40 = 4
    assert result.deepfake.is_suspicious is False
    assert result.scam_intent.scam_detected is False