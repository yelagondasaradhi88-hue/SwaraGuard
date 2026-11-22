"""
Tests for deepfake detector.
"""
import pytest
from backend.api.deepfake_detector import DeepfakeDetector


def test_detect_from_transcript_urgent():
    detector = DeepfakeDetector()
    result = detector.detect_from_transcript("Please transfer money immediately")
    assert result.synthetic_probability > 0.5
    assert result.is_suspicious is True
    assert result.is_mock is True


def test_detect_from_transcript_normal():
    detector = DeepfakeDetector()
    result = detector.detect_from_transcript("Hello, how are you today")
    assert result.is_suspicious is False
    assert result.synthetic_probability < 0.5


def test_detect_is_pydantic_model():
    from backend.api.models import DeepfakeDetectionResult
    detector = DeepfakeDetector()
    result = detector.detect_from_transcript("Hello")
    assert isinstance(result, DeepfakeDetectionResult)
    assert hasattr(result, "synthetic_probability")
