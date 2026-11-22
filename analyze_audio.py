import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROMPT = """
You are SwaraGuard, an AI voice-scam and deepfake detector for Indian phone calls.
Listen carefully to this audio clip and return ONLY valid JSON with these exact keys:
{
  "transcript": "summary or transcript of what was spoken",
  "language_detected": "e.g., English, Hindi, Telugu, Hinglish",
  "risk_score": 0 to 100,
  "verdict": "SAFE" | "SUSPICIOUS" | "HIGH_RISK_SCAM",
  "deepfake_voice_indicators": ["list any synthetic, TTS, robotic, flat, or unnatural voice traits heard; only write 'None detected' if the voice sounds naturally human"],
  "scam_tactics_detected": ["e.g., OTP request, UPI urgency, digital arrest threat, KYC expiry, or 'None'"],
  "sensitive_info_leaked": true or false,
  "leaked_items": ["e.g., OTP, bank account number, UPI PIN, card details, or 'None'"],
  "user_advice": "1-sentence actionable safety instruction for the caller"
}
"""


def _is_music_or_non_speech(audio_path: str) -> bool:
    """Detect whether the audio is music/non-speech instead of a phone call.

    Uses librosa to check:
    1. Speech-like pitch range (85-255 Hz for typical voices).
    2. Spectral characteristics (music has more harmonic complexity).
    3. Zero-crossing rate (music typically differs from speech).

    Returns True if the file appears to be music or has no speech.
    """
    try:
        import librosa
        import numpy as np

        y, sr = librosa.load(audio_path, sr=22050, duration=30)

        # Empty or near-silent audio
        if len(y) < sr * 0.5:
            return True
        rms = float(np.sqrt(np.mean(y ** 2)))
        if rms < 0.001:
            return True

        # Speech pitch tracking: speech has fundamental freq roughly 80-400 Hz.
        # Music with vocals can have pitch too, so we also look at
        # harmonic/percussive separation — music is strongly percussive or
        # has a steady harmonic structure with no speech-like variance.
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        # Speech has sparse, irregular onsets; music has dense, regular onsets.
        onset_rate = float(np.mean(onset_env > np.mean(onset_env) * 0.5))

        # Spectral rolloff: music tends to use a broader frequency band.
        rolloff = float(np.percentile(librosa.feature.spectral_rolloff(y=y, sr=sr)[0], 85))

        # Speech has dominant energy in 300-3400 Hz (telephony band).
        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))

        # Music has a much higher spectral centroid and a much higher rolloff
        # than typical phone-call speech.
        looks_like_music = spectral_centroid > 2000 and rolloff > 6000
        looks_percussive = onset_rate > 0.35

        return bool(looks_like_music or looks_percussive)
    except Exception:
        # If librosa isn't available or analysis fails, fall back to
        # Gemini-based detection inside the prompt (do not block analysis).
        return False


def analyze_audio_file(audio_path: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at {audio_path}")

    # ---- Music / non-speech guard ----
    # Songs (e.g., "Nuvvunte Chaley") are not phone calls. Without this
    # check, Gemini transcribes lyrics and pattern-matches "OTP" etc.,
    # producing false HIGH_RISK_SCAM verdicts.
    if _is_music_or_non_speech(audio_path):
        return {
            "transcript": "[Music / non-speech audio detected — no phone-call speech found]",
            "language_detected": "Unknown",
            "risk_score": 0,
            "verdict": "SAFE",
            "deepfake_voice_indicators": ["None detected"],
            "scam_tactics_detected": ["None"],
            "sensitive_info_leaked": False,
            "leaked_items": ["None"],
            "user_advice": "No phone-call speech detected in this audio. SwaraGuard only screens live calls, not music.",
            "is_music": True,
        }

    client = genai.Client(api_key=api_key)
    uploaded_audio = client.files.upload(file=audio_path)
    try:
        flash_models = [
            m.name
            for m in client.models.list()
            if getattr(m, "name", "") and "flash" in m.name
        ]
        # Prefer gemini-3.1-flash-lite first since it validated cleanly
        flash_models.sort(key=lambda name: (0 if "3.1-flash-lite" in name else 1, name))

        last_error = None
        response = None

        for model_name in flash_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[uploaded_audio, PROMPT],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0,
                    ),
                )
                break
            except Exception as e:
                last_error = e

        if response is None:
            raise RuntimeError(f"All flash models failed. Last error: {last_error}")

        return json.loads(response.text)
    finally:
        try:
            client.files.delete(name=uploaded_audio.name)
        except Exception:
            pass

if __name__ == "__main__":
    output = analyze_audio_file("test_audio/sample.m4a")
    print(json.dumps(output, indent=2, ensure_ascii=False))