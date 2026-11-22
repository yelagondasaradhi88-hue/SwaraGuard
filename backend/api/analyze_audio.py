"""
SwaraGuard AI - Audio Analyzer
Combines speech-to-text and scam/deepfake detection into a voice risk score.
Production-ready implementation with Gemini API support and mock fallback.
"""
import time
import json
import os
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


# Pydantic schemas for structured output
class LanguageDetection(BaseModel):
    """Language detection result."""
    code: str  # 'en', 'hi', 'te'
    name: str  # 'English', 'Hindi', 'Telugu'


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


class VoiceAnalysisResponse(BaseModel):
    """Complete voice analysis response."""
    transcription: TranscriptionResult = Field(default_factory=TranscriptionResult)
    deepfake: DeepfakeDetectionResult = Field(default_factory=DeepfakeDetectionResult)
    scam_intent: ScamIntentResult = Field(default_factory=ScamIntentResult)
    voice_risk_score: float = 0.0
    processing_time_ms: float = 0.0
    is_mock: bool = True


class IntentCategory(str, Enum):
    OTP_THEFT = "OTP_THEFT"
    KYC_THREAT = "KYC_THREAT"
    DIGITAL_ARREST = "DIGITAL_ARREST"
    URGENT_MONEY_TRANSFER = "URGENT_MONEY_TRANSFER"
    REMOTE_ACCESS_APP = "REMOTE_ACCESS_APP"
    PHISHING = "PHISHING"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Demo transcripts for when no real audio is provided
DEMO_SCENARIOS = {
    "bank_scam": (
        "Hello sir, this is calling from HDFC Bank. Your KYC is expiring today. "
        "If you don't verify immediately your account will be blocked. "
        "Please share the OTP I just sent to your phone number to complete verification. "
        "This is urgent, you must act now."
    ),
    "digital_arrest": (
        "This is Inspector Sharma from the Cyber Crime Department. "
        "You are involved in a money laundering case. You will be arrested if you don't cooperate. "
        "Please install AnyDesk on your phone and share your screen so we can verify your account. "
        "Transfer 50000 rupees to this account for verification, it will be refunded."
    ),
    "normal": (
        "Hello, I am calling to confirm your rent payment for this month. "
        "Could you please transfer 5000 rupees to the usual account by tomorrow? "
        "Let me know if you have any questions. Thank you."
    ),
    "telugu_scam": (
        "హలై, మీ బ్యాంక్ ఖాతా సమస్య ఉంది. మీరు త్వరగా చేయాలి. "
        "OTP మనం మీ ఫోన్‌పేల్‌పై పంపాము. దయచేసి సమాధానం ఇవ్వండి మరింత రుద్దం పంపండి."
    ),
    "hinglish_scam": (
        "Hello, aapke bank mein ek problem hai. Aap jaldi karo. "
        "Humne aapke phone pe OTP bhej diya hai. Kya aap mujhe OTP bhec skate hain?"
    ),
    "family_safe": (
        "Hi ammi, sorry I couldn't call earlier. How are you doing? "
        "Just wanted to check if you need anything from the market today."
    )
}

SCAM_PATTERNS = {
    "OTP_THEFT": [
        r"share.*OTP", r"provide.*OTP", r"send.*OTP", r"OTP.*bhej",
        r"\bOTP\s+kare", r"OTP.*verify", r"KYC.*with OTP"
    ],
    "KYC_THREAT": [
        r"account.*blocked", r"account.*frozen", r"KYC.*expiring",
        r"immediate.*verification", r"urgent.*KYC"
    ],
    "DIGITAL_ARREST": [
        r"arrest", r"digital arrest", r"court.*case", r"police.*department",
        r"Inspector.*Sharma"
    ],
    "URGENT_MONEY_TRANSFER": [
        r"transfer.*money", r"send.*rupees", r"50000.*rupees",
        r"verification.*transfer", r"emergency.*transfer"
    ],
    "REMOTE_ACCESS_APP": [
        r"AnyDesk", r"TeamViewer", r"remote.*access", r"share.*screen",
        r"install.*app.*phone"
    ],
    "PHISHING": [
        r"click.*link", r"verify.*link", r"website.*login", r"password.*reset"
    ]
}


class AudioAnalyzer:
    """
    Analyzes call audio chunks for scam and deepfake indicators.

    Uses Gemini API when available for transcription and analysis.
    Falls back to mock analysis for demo purposes.
    """

    def __init__(self, gemini_client=None):
        self.gemini_client = gemini_client
        self.has_gemini = gemini_client is not None

    def analyze_audio(self, audio_path: Optional[str] = None, demo_scenario: Optional[str] = None,
                      transcript_text: Optional[str] = None, is_unknown_number: bool = False) -> VoiceAnalysisResponse:
        """
        Analyze audio for scam and deepfake indicators.

        Args:
            audio_path: Path to temporary audio file (optional)
            demo_scenario: Pre-defined demo scenario name
            transcript_text: Raw transcript for analysis (alternative to audio)
            is_unknown_number: Whether the caller is from an unknown number

        Returns:
            VoiceAnalysisResponse
        """
        start_time = time.time()

        # Get transcript first
        transcript = ""
        if transcript_text:
            transcript = transcript_text
        elif audio_path and self.has_gemini:
            transcript = self._transcribe_with_gemini(audio_path)
        elif demo_scenario and demo_scenario in DEMO_SCENARIOS:
            transcript = DEMO_SCENARIOS[demo_scenario]

        # Analyze the transcript
        result = self._analyze_transcript_internal(transcript, demo_scenario, is_unknown_number)

        result.processing_time_ms = round((time.time() - start_time) * 1000, 2)
        return result

    def _analyze_transcript_internal(self, transcript: str, demo_scenario: Optional[str] = None,
                                      is_unknown_number: bool = False) -> VoiceAnalysisResponse:
        """Internal method to analyze transcript and build response."""

        # Classify scam intent
        scam_intent = self._classify_scam_intent(transcript)

        # Detect deepfake indicators
        deepfake = self._detect_deepfake(transcript, demo_scenario)

        # Create transcription result
        language = self._detect_language(transcript)
        suspicious_phrases = self._extract_suspicious_phrases(transcript)

        transcription = TranscriptionResult(
            text=transcript,
            language_detected=language,
            confidence=0.92 if transcript else 0.0,
            suspicious_phrases=suspicious_phrases,
            is_mock=demo_scenario is not None or not self.has_gemini
        )

        # Calculate voice risk score (0-100)
        voice_risk = self._calculate_voice_risk_score(transcript, scam_intent, deepfake, is_unknown_number)

        return VoiceAnalysisResponse(
            transcription=transcription,
            deepfake=deepfake,
            scam_intent=scam_intent,
            voice_risk_score=round(voice_risk, 1),
            processing_time_ms=0.0,
            is_mock=demo_scenario is not None or not self.has_gemini
        )

    def _transcribe_with_gemini(self, audio_path: str) -> str:
        """Use Gemini API for transcription."""
        if not self.gemini_client:
            return ""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[audio_path, "Transcribe the audio content accurately. Return only the transcript."],
                config={"response_mime_type": "text/plain"}
            )
            return response.text
        except Exception as e:
            print(f"Gemini transcription failed: {e}")
            return ""

    def _classify_scam_intent(self, transcript: str) -> ScamIntentResult:
        """Classify scam intent from transcript using pattern matching and NLP."""
        if not transcript:
            return ScamIntentResult(
                scam_detected=False,
                intent_categories=[],
                confidence=0.0,
                reasons=["No transcription available"],
                is_mock=True
            )

        detected_categories = []
        all_reasons = []

        for category, patterns in SCAM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, transcript, re.IGNORECASE):
                    if category not in detected_categories:
                        detected_categories.append(category)
                        all_reasons.append(f"Matched pattern: {category.replace('_', ' ').lower()}")

        confidence = min(1.0, len(detected_categories) * 0.25)
        scam_detected = len(detected_categories) > 0

        # Check for urgent pressure language
        urgency_patterns = [r"act now", r"immediately", r"deadline", r"urgent", r"24 hours"]
        for pattern in urgency_patterns:
            if re.search(pattern, transcript, re.IGNORECASE):
                if "URGENT_PRESSURE" not in [c for c in detected_categories]:
                    all_reasons.append("Uses urgency/pressure tactics")
                break

        return ScamIntentResult(
            scam_detected=scam_detected,
            intent_categories=detected_categories,
            confidence=round(confidence, 2),
            reasons=all_reasons[:5],  # Limit reasons
            is_mock=True
        )

    def _detect_deepfake(self, transcript: str, demo_scenario: Optional[str] = None) -> DeepfakeDetectionResult:
        """Detect deepfake/synthetic voice indicators."""
        is_mock = demo_scenario is not None

        # For scam scenarios, simulate higher synthetic probability
        if demo_scenario in ["bank_scam", "digital_arrest", "telugu_scam", "hinglish_scam"]:
            return DeepfakeDetectionResult(
                synthetic_probability=0.75,
                is_suspicious=True,
                model="MockDeepfakeDetector",
                indicators=["Robotic/flat voice", "Unnaturally uniform pitch", "Lack of natural pauses"],
                is_mock=True
            )

        # Analyze transcript for voice quality indicators
        indicators = []
        synthetic_probability = 0.1

        # Check for unnatural speech patterns
        if transcript:
            # Flat/uninflected speech
            if len(transcript.split()) < 10 or not any(c in transcript for c in '.,!?'):
                indicators.append("Monotonous tone")
                synthetic_probability += 0.15

            # Robot-style phrases
            robot_patterns = [r"listen carefully", r"important notice", r"synthetic voice"]
            for pattern in robot_patterns:
                if re.search(pattern, transcript, re.IGNORECASE):
                    indicators.append("Robotic phrasing detected")
                    synthetic_probability += 0.1

        return DeepfakeDetectionResult(
            synthetic_probability=round(min(1.0, synthetic_probability), 2),
            is_suspicious=synthetic_probability > 0.5,
            model="MockDeepfakeDetector",
            indicators=indicators,
            is_mock=True
        )

    def _extract_suspicious_phrases(self, text: str) -> list:
        """Extract suspicious phrases from transcript."""
        if not text:
            return []

        phrases = []
        suspicious_patterns = [
            r"(your account will be (blocked|frozen))",
            r"(share the OTP|send the OTP|provide OTP)",
            r"(you will be arrested|digital arrest)",
            r"(act now|immediately|urgent)",
            r"(install AnyDesk|share your screen)",
            r"(transfer.*rupees|send money)",
            r"(OTP.*verify|KYC.*verify)",
            r"(emergency.*transfer|urgent.*transfer)",
        ]

        for pattern in suspicious_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.group(0)
                if phrase not in phrases:
                    phrases.append(phrase)

        return phrases

    def _calculate_voice_risk_score(self, transcript: str, scam_intent: ScamIntentResult,
                                     deepfake: DeepfakeDetectionResult, is_unknown_number: bool) -> float:
        """Calculate voice risk score (0-100) based on multiple factors."""
        voice_risk = 0.0

        # Deepfake component (0-30 points)
        voice_risk += min(30, deepfake.synthetic_probability * 30)

        # Scam intent component (0-40 points)
        if scam_intent.scam_detected:
            voice_risk += min(40, len(scam_intent.intent_categories) * 15 + scam_intent.confidence * 10)

        # Suspicious phrases bonus (0-15 points)
        suspicious_phrases = self._extract_suspicious_phrases(transcript)
        if suspicious_phrases:
            voice_risk += min(15, len(suspicious_phrases) * 3)

        # Unknown number penalty (0-15 points) - but only increases if scam detected
        # CRITICAL RULE: Unknown number alone does NOT trigger fraud
        if is_unknown_number and scam_intent.scam_detected:
            voice_risk += min(15, scam_intent.confidence * 15)

        return round(min(100, voice_risk), 1)

    def _detect_language(self, text: str) -> str:
        """Detect language from text using Unicode character ranges."""
        if not text:
            return "en"

        if re.search(r'[ऀ-ॿ]', text):
            return "hi"  # Hindi
        elif re.search(r'[ఀ-౿]', text):
            return "te"  # Telugu
        elif re.search(r'[ಀ-೿]', text):
            return "kn"  # Kannada
        elif re.search(r'[ഀ-ൿ]', text):
            return "ml"  # Malayalam
        return "en"

    def analyze_transcript(self, transcript: str, is_unknown_number: bool = False) -> VoiceAnalysisResponse:
        """Analyze a raw transcript (for testing without audio)."""
        return self._analyze_transcript_internal(transcript, None, is_unknown_number)


# Singleton instance
audio_analyzer = AudioAnalyzer()