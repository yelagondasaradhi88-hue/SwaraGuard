# SwaraGuard Architecture

## Text-Based Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SWARAGUARD SYSTEM                                   │
└────────────────────────┬────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌───────────────┐              ┌───────────────────────┐
│  ANDROID APP  │              │   FASTAPI BACKEND     │
│  (Kotlin)     │◄────────────►│   (Python 3.9)        │
└───────┬───────┘   HTTPS     └─────────────┬─────────┘
        │                                   │
        │ 1. Foreground Service             │ 1. Risk Engine
        │    - CallAnalysisService          │    - Scoring Logic
        │    - Audio chunking (3-5s)        │    - Scam detection
        │    - Speakerphone mic capture     │    - Deepfake detection
        │    - TelecomManager.endCall()     │    - Simulated freeze
        │                                   │
        │ 2. Activity Flow                  │ 2. API Endpoints
        │    - MainActivity                 │    - /api/analyze
        │    - DemoModeActivity             │    - /api/simulate-freeze
        │    - ProtectionFlowActivity       │    - /api/protection-flow
        │    - Permission handling          │    - /api/dashboard
        │    - Risk indicators              │
        │                                   │
        │ 3. Local Models (Optional)        │ 3. Deepfake Models
        │    - AASIST (offline)             │    - AASIST
        │    - RawNet2 (offline)            │    - RawNet2
        │    - Vosk for STT                 │    - Gemini API (primary, cloud)
        │                                   │
        └───────────────────────────────────┘

DATA FLOW:
═════════

CALL FLOW (Live):
1. Android detects incoming call via READ_PHONE_STATE
2. User accepts call → CallAnalysisService starts
3. Audio captured from MIC (speakerphone mode required for Android 10+)
4. Audio split into 3-5 second chunks
5. Each chunk sent to FastAPI backend via HTTPS
6. Backend analyzes with Gemini API:
   - Transcription (English/Hindi/Telugu)
   - Deepfake probability
   - Scam tactics detection
   - Risk scoring
7. Risk level determined:
   - Low (0-39): Continue monitoring
   - Medium (40-69): Show warning notification
   - High (70-100): Start countdown → end call via TelecomManager
8. If sensitive info leaked during call: Initiate protection flow

DEMO MODE:
1. User selects pre-recorded audio file
2. File uploaded to /api/analyze
3. Same analysis pipeline
4. Results displayed with risk indicators

PROTECTION FLOW:
1. User taps "Activate Protection"
2. POST /api/simulate-freeze called
3. Backend simulates bank account lock (24h)
4. Dashboard updated via /api/dashboard
5. User guided to:
   - Call 1930 (emergency helpline)
   - Open bank app lock screen
   - Send pre-filled SMS to bank

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            COMPONENT DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                              │
├─────────────────────────────────────────────────────────────────────┤
│  routes/main.py                                                     │
│  ├── POST /api/analyze          → FastAPIRouter                     │
│  │     ├── analyze_audio_file()                                     │
│  │     └── Risk engine scoring                                      │
│  ├── POST /api/simulate-freeze  → Simulate Bank Freeze              │
│  ├── POST /api/protection-flow  → Full Protection Integration       │
│  ├── GET  /api/dashboard        → Active Locks & Stats              │
│  └── GET  /api/health           → Service Health Check              │
│                                                                     │
│  services/analyze_service.py   → Audio File Analysis                │
│  ├── Gemini API client (primary)                                    │
│  ├── Fallback analysis (demo mode)                                  │
│  ├── ASVspoof models (future)                                       │
│  └── Whisper/AI4Bharat STT (multilingual)                           │
│                                                                     │
│  services/bank_service.py    → Mock Bank System                     │
│  ├── Transaction lock simulation                                    │
│  ├── UPI app URL deep links                                         │
│  └── SMS templates                                                  │
│                                                                     │
│  utils/risk_engine.py        → Risk Scoring Logic                   |
│  ├── Deepfake probability (0-30 pts)                                │
│  ├── Scam tactics count (0-40 pts)                                  │
│  ├── Sensitive info leaked (0-20 pts)                               │
│  └── Combined risk_score (Low/Medium/High)                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         ANDROID APP                                 │
├─────────────────────────────────────────────────────────────────────┤
│  MainActivity.kt                                                    │
│  ├── Permission handling (RECORD_AUDIO, POST_NOTIFICATIONS)         │
│  ├── Risk indicator UI (0-100 score visual)                         │
│  ├── Start/Stop analysis button                                     │
│  └── Demo mode launcher                                             │
│                                                                     │
│  CallAnalysisService.kt (Foreground Service)                        │
│  ├── AudioRecord from MIC                                           │
│  ├── WAV file chunking (3-5s)                                       │
│  ├── Multipart upload to backend                                    │
│  ├── Risk callback handling                                         │
│  └── TelecomManager.endCall() on HIGH risk                          │
│                                                                     │
│  DemoModeActivity.kt                                                │
│  ├── Load sample audio from assets                                  │
│  ├── MediaPlayer playback                                           │
│  ├── Analyze button                                                 │
│  └── Display results                                                │
│                                                                     │
│  ProtectionFlowActivity.kt                                          │
│  ├── Simulated bank freeze UI                                       │
│  ├── 1930 helpline dialer                                           │
│  ├── Bank app deep link launcher                                    │
│  ├── Pre-filled SMS composer                                        │
│  └── Dashboard redirect                                             │
│                                                                     │
│  widget/RiskIndicatorView.kt                                        │
│  ├── Circular progress indicator (0-100)                            │
│  ├── Color-coded risk levels (red/orange/green)                     │
│  └── Animated score updates                                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                           │
├─────────────────────────────────────────────────────────────────────┤
│  Gemini AI API (Google)                                             │
│  ├── gemini-1.5-flash (speech analysis)                             │
│  ├── gemini-pro-vision (optional video)                             │
│  └── Free tier: 600 requests/min, 1M characters/day                 │
│                                                                     │
│  Network Integration                                                │
│  ├── Retrofit + OkHttp                                              │
│  ├── JSON/Gson serialization                                        │
│  └── HTTPS with certificate pinning (production)                    │
└─────────────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/` | GET | Serve dashboard | - |
| `/health` | GET | Health check | - |
| `/api/analyze` | POST | Analyze audio file | 10/min |
| `/api/simulate-freeze` | POST | Freeze account (simulated) | 5/hr |
| `/api/protection-flow` | POST | Full protection flow | 3/hr |
| `/api/dashboard` | GET | Get active locks | 30/min |
| `/api/lock-status` | GET | Check lock status | 60/min |
| `/api/deepfake-models` | GET | List available models | Unlimited |
| `/api/scanners` | GET | List scanners | Unlimited |
| `/api/helpline` | GET | Get helpline info | Unlimited |