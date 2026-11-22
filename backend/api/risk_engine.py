"""
SwaraGuard AI - Risk Engine
Combines voice, device, and transaction risk scores into a unified risk score.
"""
from typing import Any, Dict, List


class RiskEngine:
    """Core risk calculation engine for SwaraGuard."""

    def calculate_voice_risk(self, voice_risk_score: float, deepfake_prob: float = 0.0, scam_tactics_count: int = 0) -> float:
        """Calculate voice risk score (0-100)."""
        score = 0.0
        # Deepfake component (0-40 points)
        score += min(40, deepfake_prob * 40)
        # Scam tactics component (0-40 points)
        if scam_tactics_count >= 3:
            score += 40
        elif scam_tactics_count == 2:
            score += 30
        elif scam_tactics_count == 1:
            score += 15
        # Use the provided voice_risk_score as base if higher
        return round(min(100, max(score, voice_risk_score)), 1)

    def calculate_device_risk(self, device_events: List[Dict[str, Any]]) -> float:
        """Calculate device risk score (0-100)."""
        score = 0
        for event in device_events:
            score += event.get('risk_points', 0)
        return round(min(100, score), 1)

    def calculate_transaction_risk(self, locked: bool = False, transaction_count: int = 0, amount: float = 0) -> float:
        """Calculate transaction risk score (0-100)."""
        score = 0
        if locked:
            score += 30
        if transaction_count > 3:
            score += 20
        if amount > 10000:
            score += 15
        return round(min(100, score), 1)

    def combine_risk_scores(self, voice_risk: float, device_risk: float, transaction_risk: float) -> Dict[str, Any]:
        """
        Combine risk scores into unified score.

        Weights: 40% voice, 40% device, 20% transaction.
        """
        combined = voice_risk * 0.4 + device_risk * 0.4 + transaction_risk * 0.2
        combined = round(min(100, combined), 1)

        if combined >= 80:
            level = "CRITICAL"
            action = "PROTECT_ACCOUNT"
        elif combined >= 60:
            level = "HIGH"
            action = "WARN_AND_PROTECT"
        elif combined >= 30:
            level = "MEDIUM"
            action = "WARN"
        else:
            level = "LOW"
            action = "MONITOR"

        return {
            "risk_score": combined,
            "risk_level": level,
            "recommended_action": action,
        }

    def build_signals(self, voice_risk: float, device_risk: float,
                      transaction_risk: float, voice_signals: List[str],
                      device_signals: List[str], transaction_signals: List[str]) -> List[str]:
        """Build human-readable list of risk signals."""
        signals = []

        if voice_risk > 0:
            for s in voice_signals[:3]:
                signals.append(s)

        if device_risk > 0:
            for s in device_signals[:3]:
                signals.append(s)

        if transaction_risk > 0:
            for s in transaction_signals[:3]:
                signals.append(s)

        return signals if signals else ["No significant risk signals detected"]


risk_engine = RiskEngine()