# 🛡️ Fraud Call Shield

> **Hackathon Prototype for Real-Time Telemetry-Based Scam Defense & Outgoing Payment Freezing**

---

## 📌 1. Project Idea & Overview

Scammers call victims and walk them through a manipulative chain of actions:
1. Open a phishing or APK download link sent via SMS / WhatsApp.
2. Install a malicious APK or weaponized remote-access tool (AnyDesk, TeamViewer, QuickSupport).
3. Grant hazardous Accessibility or Device Admin permissions.
4. Turn on screen sharing.
5. Intercept or read out a One-Time Password (OTP).
6. Open their banking app and transfer life savings to a scammer account.

### Why Existing Solutions Fall Short
Modern mobile operating systems strictly restrict or prohibit recording and transcribing private telephone calls. Solutions relying on speech transcription face privacy violations, device policy bans, heavy battery drain, and latency delays.

### The Fraud Call Shield Breakthrough
**We do NOT record, transcribe, or store audio.** Instead, we monitor the lightweight **chain of risky device telemetry events** around the user, maintain an aggregated risk score in a **sliding 15-minute time window**, and **freeze OUTGOING transfers within milliseconds** *before the money ever leaves the account*. 

- **Outgoing Transfers Only:** Incoming credits and deposits are never blocked.
- **Automated Rapid Recovery:** The bank automatically schedules a safety verification callback, or the designated Family Guardian can approve release with a single tap.
- **Privacy First:** 100% on-device simulated event flags, zero call listening, zero real PII.

---

## 🏗️ 2. System Architecture

```text
+-----------------------------------------------------------------------------------+
|                            VICTIM MOBILE DEVICE (CLIENT)                          |
|                                                                                   |
|  [Incoming Call]  --->  [Link Clicked]  --->  [App Sideload]  --->  [AnyDesk]    |
|         |                     |                     |                  |          |
|  [Screen Sharing] --->  [OTP Received]  --->  [Bank App Open] ---> [Transfer]    |
+-----------------------------------------------------------------------------------+
                                          |
                REST Telemetry & Transfer | (Sub-10ms JSON Payloads)
                                          v
+-----------------------------------------------------------------------------------+
|                         FRAUD CALL SHIELD GATEWAY (API)                           |
|                                                                                   |
|   +-----------------------+              +------------------------------------+   |
|   |   FastAPI Endpoints   | <----------> |     Risk Scoring Engine (<10ms)    |   |
|   |  (/device-event,      |              |  - 15-Minute Sliding Window        |   |
|   |   /transfer, etc.)    |              |  - Event Deduplication             |   |
|   +-----------------------+              |  - 1.3x Velocity Multiplier        |   |
|               |                          |  - Pure rule-based calculation     |   |
|               v                          +------------------------------------+   |
|   +-----------------------+                                                       |
|   |  Mock Bank State      |                                                       |
|   |  - Active / Frozen    |                                                       |
|   |  - Audit Trail        |                                                       |
|   +-----------------------+                                                       |
+-----------------------------------------------------------------------------------+
        |                                                           |
        v                                                           v
+----------------------------------+             +----------------------------------+
|      SIMULATED BANK CALLBACK     |             |      FAMILY GUARDIAN PORTAL      |
|  - Operator Verification Script  |             |  - SMS / Push Alert Notification |
|  - 2 Identity Security Questions |             |  - 1-Click Approve / Keep Frozen |
+----------------------------------+             +----------------------------------+
```

---

## 📊 3. Event Scoring & Rules Table

Events are tracked inside a **sliding 15-minute window**. Events older than 15 minutes are discarded. Distinct event points are summed and capped at **100**.

| Telemetric Event Identifier | Points | Description & Detection Heuristic |
|:---|:---:|:---|
| `unknown_call_active` | **+25** | Phone is in active call with a number not in victim's address book. |
| `link_opened` | **+15** | Browser opened from external intent (SMS, chat, email). |
| `phishing_link_detected` | **+30** | URL matches suspicious TLD (`.xyz`, `.top`, `.click`), URL shortener, or bank look-alike (`sbi-kyc-update`). |
| `apk_sideloaded` | **+30** | Package installed from unknown sources / non-Play Store provider. |
| `remote_access_app_installed_or_opened` | **+35** | AnyDesk, TeamViewer, QuickSupport, AirDroid launched. |
| `accessibility_or_device_admin_permission_granted` | **+30** | Dangerous system-level automation permission granted to 3rd party app. |
| `screen_sharing_started` | **+25** | `MediaProjection` or display capture session active. |
| `otp_received_during_risky_session` | **+20** | Inbound banking/transaction SMS arrived while risky apps/calls are open. |
| `bank_app_opened_after_risky_events` | **+10** | Mobile banking app launched directly following suspicious events. |
| `new_payee` | **+15** | Transfer destination is not in victim's `known_payees` whitelist. |
| `large_amount` | **+20** | Requested transfer is $> 3\times$ user's `typical_max_transfer` ($> \text{₹}15,000$). |
| `protected_user` | **+10** | Elderly or flagged vulnerable account profile (applies if any risk event exists). |
| `keyword_flag` | **+5 each** (max +20) | Consented on-device audio keyword match (*"safe account"*, *"arrest"*, *"OTP"*). |
| `voice_deepfake_suspected` | **+20** | Non-blocking background anti-spoofing / synthetic voice stub signal. |

### 🚀 Velocity Multiplier ($\times 1.3$)
If **3 or more distinct risky events** occur within any **10-minute interval**, a **1.3x multiplier** is applied to reflect rapid attacker-guided coercion.

---

## 🚦 4. Threat Tiers & Actions

Evaluated on every incoming telemetry signal and transfer request:

| Risk Score | Tier | Automated Defensive Action Taken |
|:---:|:---:|:---|
| **0 – 29** | `NORMAL` | Standard baseline monitoring. Payments allowed without friction. |
| **30 – 49** | `WARN` | In-app visual warning displayed: *"Banks never ask you to install apps or share your screen."* |
| **50 – 69** | `SOFT_PROTECT` | Step-up security question enforced on transfer. Family guardian notified. |
| **70 – 100** | `FREEZE` | **Outgoing transfers frozen for 30 minutes.** Incoming credits remain open. Bank callback scheduled. Guardian notified. Executed once per threat window. |

---

## 🗂️ 5. Project Structure

```text
fraud-call-shield/
├── api/
│   ├── __init__.py
│   ├── main.py            # FastAPI app, REST endpoints, CORS, tier enforcement
│   ├── models.py          # Pydantic schema validation for requests and responses
│   ├── risk_engine.py     # Pure mathematical scoring engine (<10ms runtime)
│   └── state.py           # In-memory mock bank state, audit logs, auto-unfreeze
├── ui/
│   ├── __init__.py
│   └── app.py             # Streamlit 3-tab interactive demo UI
├── tests/
│   ├── __init__.py
│   └── test_scenarios.py  # 9 automated scenarios & executive benchmark reporter
├── requirements.txt
└── README.md
```

---

## ⚡ 6. Quick Start & Run Commands

### 1. Install Dependencies
```bash
cd "fraud-call-shield"
pip install -r requirements.txt
```

### 2. Start the Mock Bank API (Terminal 1)
```bash
uvicorn api.main:app --reload --port 8000
```
*API docs available at: `http://127.0.0.1:8000/docs`*

### 3. Launch the Streamlit Demo UI (Terminal 2)
```bash
streamlit run ui/app.py
```
*Demo opens in browser at `http://localhost:8501`*

### 4. Run the 9 Test Scenarios & Benchmark Table (Terminal 3)
```bash
python tests/test_scenarios.py
# Or with pytest:
pytest tests/test_scenarios.py -s
```

---

## 📈 7. Automated Test Results & Benchmark

Run output from `tests/test_scenarios.py`:

```text
======================================================================================================
                     FRAUD CALL SHIELD - HACKATHON BENCHMARK REPORT
======================================================================================================
#   | Scenario                                   | Category       | Status | Latency 
------------------------------------------------------------------------------------------------------
1   | 1. Full Scam Sequence (40k transfer attemp | ATTACK         | PASS   |  34.36 ms
2   | 2. Normal Rent Payment (Known Payee)       | BENIGN         | PASS   |   2.79 ms
3   | 3. Family Call & Routine Grocery Payment   | BENIGN         | PASS   |   3.91 ms
4   | 4. Trusted App / Benign Link Opened        | BENIGN         | PASS   |   1.12 ms
5   | 5. Single Link Opened (No Call)            | BENIGN         | PASS   |   1.13 ms
6   | 6. Unknown Call + Link + New Payee (6k)    | SUSPICIOUS     | PASS   |   3.46 ms
7   | 7. Freeze -> Reject -> Bank Callback Unfre | RECOVERY       | PASS   |   5.26 ms
8   | 8. Guardian Authorization (Deny vs Approve | RECOVERY       | PASS   |   1.87 ms
9   | 9. Temporal Window Expiry (>15 min dropped | SLIDING_WINDOW | PASS   |   3.93 ms
======================================================================================================
                                   METRICS SUMMARY
------------------------------------------------------------------------------------------------------
  • Scams Caught (True Positives)       : 2 / 2 (100%)
  • Scams Missed (False Negatives)      : 0 (0%)
  • False Alarms on Benign Flows (FP)   : 0 (0%)
  • Average Event-to-Decision Latency   : 6.43 ms (Target: < 100 ms)
======================================================================================================
```

---

## ⚠️ 8. Limitations & Assumptions

1. **Simulated Device Events:** In this prototype, mobile events are emitted through API calls or demo UI triggers. In production, an on-device Android daemon/SDK (AccessibilityService, TelephonyManager, UsageStatsManager) would emit these signals.
2. **Platform Restrictions:**
   - **Android:** Requires explicit user permissions (Accessibility, Usage Access) and Google Play Store policy justification for financial accessibility services.
   - **iOS:** Apple's sandboxing severely restricts inter-app observability (screen recording detection exists, but background call metadata and app installation telemetry are heavily sandboxed).
3. **Mock Bank Integration:** All banking accounts, payee lists, and balance ledgers are simulated in memory. Production deployment requires secure ISO 20022 / Open Banking webhooks or core banking API integration.
4. **Initial Rule Weights:** Current point assignments are initial heuristics. In enterprise production, weights should be dynamically calibrated using logistic regression or gradient-boosted decision trees trained on anonymized fraud incident logs.

---

## 🔮 9. Future Scope & Production Roadmap

- **Core Banking Webhook Integration:** Standardized pre-authorization webhook (e.g. UPI / SEPA / FedNow risk evaluation gate).
- **On-Device Machine Learning:** Local quantized TFLite/ONNX model evaluating sequential event graphs without raw telemetry leaving the handset.
- **Enterprise URL Reputation:** Integration with Google Safe Browsing / Cloudflare Radar APIs for real-time domain age and threat intelligence.
- **Consented Voice Anti-Spoofing:** Background evaluation of caller acoustics against known synthetic voice / deepfake acoustic models.
- **Biometric Challenge & FIDO2:** Biometric liveness check as an unfreeze alternative for tech-savvy users alongside bank callbacks.

---

## 🗣️ Presentation Talking Points for the Team

> 1. *"This is a working prototype with a mock bank; phone telemetric signals are simulated cleanly without privacy risks."*
> 2. *"We do NOT record or transcribe calls. We detect the scammer-guided action sequence and freeze outgoing payments within seconds before funds leave the bank."*
> 3. *"We freeze outgoing transfers only. Legitimate incoming funds are never blocked, and rapid recovery is guaranteed through the bank callback or family guardian approval."*
