"""
Pure-function rule-based Risk Engine for Fraud Call Shield.
Evaluates telemetric device events within a sliding 15-minute window
and computes fraud risk score (0-100), alert tier, and human-readable reasons.
Designed to execute in <10ms without external blocking network calls.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import urllib.parse
import re

# Base scoring weights for device events
EVENT_POINTS: Dict[str, int] = {
    "unknown_call_active": 25,
    "link_opened": 15,
    "phishing_link_detected": 30,
    "apk_sideloaded": 30,
    "remote_access_app_installed_or_opened": 35,
    "accessibility_or_device_admin_permission_granted": 30,
    "screen_sharing_started": 25,
    "otp_received_during_risky_session": 20,
    "bank_app_opened_after_risky_events": 10,
    "new_payee": 15,
    "large_amount": 20,
    "protected_user": 10,
    "voice_deepfake_suspected": 20,
}

# Remote desktop / remote management apps frequently weaponized by scammers
KNOWN_REMOTE_DESKTOP_APPS = {
    "anydesk",
    "teamviewer",
    "quicksupport",
    "airdroid",
    "zoho assist",
    "rustdesk",
    "vnc viewer"
}

# Suspicious TLDs and shorteners
SUSPICIOUS_TLDS = {".xyz", ".top", ".click", ".link", ".live", ".work", ".loan", ".club"}
URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "cutt.ly"}

# Target bank look-alikes or KYC scam keywords in domain/URL paths
PHISHING_KEYWORDS = [
    "sbi-kyc",
    "kyc-update",
    "hdfc-verify",
    "icici-security",
    "bank-login",
    "verify-account",
    "pan-update",
    "aadhaar-kyc",
    "electricity-bill-update",
    "reward-points-claim",
    "apk-download"
]


def check_url(url: str) -> bool:
    """
    Evaluates whether a URL matches known phishing, suspicious TLD, or scam patterns.
    Pure, fast regex and string matching with zero external network dependencies.
    """
    if not url:
        return False
    
    clean_url = url.strip().lower()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "http://" + clean_url

    parsed = urllib.parse.urlparse(clean_url)
    hostname = (parsed.hostname or "").lower()
    path_and_query = (parsed.path + "?" + parsed.query).lower()

    # 1. Suspicious shortener
    if any(shortener in hostname for shortener in URL_SHORTENERS):
        return True

    # 2. Suspicious TLD
    if any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS):
        return True

    # 3. Phishing keywords in hostname or path
    for kw in PHISHING_KEYWORDS:
        if kw in hostname or kw in path_and_query:
            return True

    # 4. Raw IP address as hostname (e.g., http://192.168.1.1/kyc.apk)
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        return True

    return False


def deepfake_score(audio_path: Optional[str] = None) -> float:
    """
    Stub for background voice deepfake / anti-spoofing detection.
    In production: Runs an inference model (e.g., AASIST, RawNet, Whisper classifier)
    asynchronously without blocking the real-time device event evaluation loop.
    Returns: Confidence score between 0.0 and 1.0.
    """
    if audio_path and "deepfake" in audio_path.lower():
        return 0.88
    # Baseline benign mock value
    return 0.05


def determine_tier(score: int) -> str:
    """
    Maps risk score (0-100) to operational response tier:
      < 30    : NORMAL
      30 - 49 : WARN
      50 - 69 : SOFT_PROTECT
      70+     : FREEZE
    """
    if score >= 70:
        return "FREEZE"
    elif score >= 50:
        return "SOFT_PROTECT"
    elif score >= 30:
        return "WARN"
    return "NORMAL"


def evaluate_risk(
    events: List[Dict[str, Any]],
    protected_user: bool = True,
    typical_max_transfer: float = 5000.0,
    current_time: Optional[datetime] = None,
    window_minutes: int = 15
) -> Dict[str, Any]:
    """
    Core risk scoring function.
    - Filters to events within the sliding 15-minute window.
    - Deduplicates distinct event types for point summation.
    - Applies keyword flags (up to +20).
    - Applies protected_user (+10) if any other risky event exists.
    - Applies 1.3x multiplier if 3+ distinct risky event types occurred within any 10-minute window.
    - Produces chronological human-readable explanation reasons.
    """
    now = current_time or datetime.now(timezone.utc)
    cutoff_seconds = window_minutes * 60

    # 1. Filter events within sliding window (15 minutes)
    valid_events: List[Dict[str, Any]] = []
    for ev in events:
        ts = ev.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts is None:
            ts = now
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        delta = (now - ts).total_seconds()
        # Keep if within past 15 minutes and not in the far future
        if 0 <= delta <= cutoff_seconds:
            valid_events.append({**ev, "dt": ts})

    # Sort chronologically
    valid_events.sort(key=lambda x: x["dt"])

    # 2. Extract distinct event types and process special cases
    distinct_types: Set[str] = set()
    keyword_flags_found: Set[str] = set()
    has_risky_device_event = False

    for ev in valid_events:
        etype = ev.get("event_type", "")
        details = ev.get("details", {}) or {}

        # URL phishing detection on link_opened
        if etype == "link_opened":
            distinct_types.add("link_opened")
            has_risky_device_event = True
            url = details.get("url", "")
            if check_url(url):
                distinct_types.add("phishing_link_detected")
        elif etype == "phishing_link_detected":
            distinct_types.add("phishing_link_detected")
            has_risky_device_event = True
        elif etype == "keyword_flag":
            kw = details.get("keyword") or details.get("phrase")
            if kw:
                keyword_flags_found.add(str(kw).lower())
            else:
                keyword_flags_found.add("suspicious_call_keyword")
            has_risky_device_event = True
        elif etype in EVENT_POINTS:
            distinct_types.add(etype)
            if etype not in ("new_payee", "large_amount", "protected_user"):
                has_risky_device_event = True

    # 3. Compute base points
    base_score = 0
    reasons_list: List[str] = []

    for etype in sorted(distinct_types):
        pts = EVENT_POINTS.get(etype, 0)
        base_score += pts

    # Handle keyword flags: +5 each, max +20
    kw_points = min(20, len(keyword_flags_found) * 5)
    base_score += kw_points

    # Protected user: +10 if any other risky event exists
    if protected_user and (has_risky_device_event or "new_payee" in distinct_types or "large_amount" in distinct_types):
        base_score += EVENT_POINTS["protected_user"]
        distinct_types.add("protected_user")

    # 4. Check for 1.3x multiplier (3+ distinct risky events within any 10-minute / 600s interval)
    multiplier_applied = False
    risky_event_types_pool = {
        "unknown_call_active", "link_opened", "phishing_link_detected",
        "apk_sideloaded", "remote_access_app_installed_or_opened",
        "accessibility_or_device_admin_permission_granted",
        "screen_sharing_started", "otp_received_during_risky_session",
        "bank_app_opened_after_risky_events", "voice_deepfake_suspected"
    }

    # Sliding 10-minute check over valid_events
    for i, ev_start in enumerate(valid_events):
        t0 = ev_start["dt"]
        sub_distinct = set()
        for ev_next in valid_events[i:]:
            if (ev_next["dt"] - t0).total_seconds() <= 600:
                t = ev_next.get("event_type")
                if t in risky_event_types_pool:
                    sub_distinct.add(t)
                if t == "link_opened" and check_url((ev_next.get("details") or {}).get("url", "")):
                    sub_distinct.add("phishing_link_detected")
        if len(sub_distinct) >= 3:
            multiplier_applied = True
            break

    total_score = base_score
    if multiplier_applied:
        total_score = int(round(total_score * 1.3))

    total_score = max(0, min(100, total_score))
    tier = determine_tier(total_score)

    # 5. Build human-readable chronological summary
    event_human_labels = {
        "unknown_call_active": "Unknown call active",
        "link_opened": "Link opened",
        "phishing_link_detected": "Phishing link detected",
        "apk_sideloaded": "Untrusted APK sideloaded",
        "remote_access_app_installed_or_opened": "Remote-access app (AnyDesk/TeamViewer) opened",
        "accessibility_or_device_admin_permission_granted": "Accessibility/Device Admin granted",
        "screen_sharing_started": "Screen sharing active",
        "otp_received_during_risky_session": "OTP received during suspicious call session",
        "bank_app_opened_after_risky_events": "Bank app opened following risky device triggers",
        "new_payee": "Transfer to an unverified new payee",
        "large_amount": "Transfer amount significantly exceeds typical maximum",
        "protected_user": "Account flagged under Enhanced Protection",
        "voice_deepfake_suspected": "Synthetic/Deepfake voice pattern flagged on call"
    }

    chain_labels = []
    for ev in valid_events:
        lbl = event_human_labels.get(ev["event_type"])
        if lbl and lbl not in chain_labels:
            chain_labels.append(lbl)

    if valid_events:
        t_first = valid_events[0]["dt"]
        t_last = valid_events[-1]["dt"]
        duration_mins = max(1, int((t_last - t_first).total_seconds() // 60))
        if len(chain_labels) >= 2:
            reasons_list.append(f"{', then '.join(chain_labels)} within {duration_mins} minute{'s' if duration_mins != 1 else ''}.")
        elif chain_labels:
            reasons_list.append(f"{chain_labels[0]} detected in active session.")
    
    if keyword_flags_found:
        reasons_list.append(f"Scam conversational keywords detected: {', '.join(sorted(keyword_flags_found))}.")

    if multiplier_applied:
        reasons_list.append("Rapid multi-step scam progression detected (1.3x velocity multiplier applied).")

    if not reasons_list:
        reasons_list.append("No suspicious device anomalies detected in recent window.")

    return {
        "score": total_score,
        "base_score": base_score,
        "tier": tier,
        "multiplier_applied": multiplier_applied,
        "distinct_events": list(distinct_types),
        "reasons": reasons_list,
        "valid_event_count": len(valid_events),
    }
