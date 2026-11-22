# SwaraGuard - AI-Powered Scam Call Protection

**Track: AI & Generative AI | Hackathon Project | Team SonicSentinels**

## Overview

Fraudsters increasingly use AI voice cloning and real-time voice translation from unknown numbers to imitate a victim's own family members—alongside fake bank or authority scripts—to create panic and steal OTPs, UPI PINs, or money. However, blindly blocking all unknown numbers fails in real life because a genuine family member may call from a new mobile number and must never be blocked. SwaraGuard solves this by analyzing what happens inside the call—keeping genuine calls from a family member's new number completely SAFE with zero blocking, while detecting synthetic/AI-cloned voice cues, suspicious scam intent, and credential requests to flag fraud, guide users with a simulated bank hold and 1930 helpline workflow, and move toward auto-disconnect in our next mobile build.

SwaraGuard is an AI-powered scam call detection platform with:
- **Live Analysis Mode**: Real-time scam detection during active calls
- **Demo Mode**: Analyze pre-recorded audio files
- **Protection Flow**: Simulated bank freeze with emergency actions
- **Web Dashboard**: Full threat assessment interface

## Live Demo

- **Production**: https://deepfake-scam-protection.netlify.app/
- **Local Dev**: Run `uvicorn main:app --reload --port 8000`

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                               │
├─────────────────────────────────────────────────────────────────────┤
│  routes/main.py                                                     │
│  ├── POST /api/analyze          → Audio analysis via Gemini AI     │
│  ├── POST /api/simulate-freeze  → Simulated bank freeze (15 min)   │
│  ├── GET  /                     → Home page                      │
│  ├── GET  /login                → Authentication page            │
│  ├── GET  /dashboard            → Web dashboard                  │
│  ├── GET  /analysis             → Call analysis interface        │
│  └── GET  /protection           → Emergency protection panel     │
└─────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Mock Bank System (SQLite)                        │
│  - Integer paise math (1 INR = 100 paise)                          │
│  - ACID atomic transfers                                           │
│  - Pre-seeded demo accounts: ACC-IND-1001, ACC-IND-1002, ACC-IND-1003│
└─────────────────────────────────────────────────────────────────────┘

Web Dashboard: Dark slate/navy theme with cyan/blue accents
Mobile App: Android 10+ with foreground service
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full diagram.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for web-designs)
- Android Studio (for mobile app development)
- Google Gemini API Key

### Backend

```bash
# Navigate to project root
cd "/Users/saradhi/untitled folder1/SwaraGuard"

# Activate virtual environment
source .venv/bin/activate

# Set up environment
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the server
python main.py
# Or: uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Web Frontend

The web dashboard is served by the FastAPI backend. Access at:

- **Home**: http://localhost:8000/
- **Login**: http://localhost:8000/login
- **Dashboard**: http://localhost:8000/dashboard
- **Analysis**: http://localhost:8000/analysis
- **Protection**: http://localhost:8000/protection

### Android App

```bash
# Open Android Studio and import:
# File → Open → "/Users/saradhi/untitled folder1/SwaraGuard/android"

# Or build via CLI
cd "/Users/saradhi/untitled folder1/SwaraGuard/android"
./gradlew assembleDebug
```

See [HACKATHON_BUILD_GUIDE.md](./HACKATHON_BUILD_GUIDE.md) for detailed build instructions.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve home page |
| `/login` | GET | Serve login page |
| `/dashboard` | GET | Serve web dashboard |
| `/analysis` | GET | Serve analysis page |
| `/protection` | GET | Serve protection page |
| `/api/analyze` | POST | Analyze audio file for deepfake/scam |
| `/api/simulate-freeze` | POST | Simulated bank freeze (15 min) |

### Analyze Call Audio

```bash
curl -X POST -F "file=@test_audio/sample.m4a" http://localhost:8000/api/analyze
```

Response:
```json
{
  "risk_score": 95,
  "risk_level": "high",
  "transcript": "Hello sir, I am calling from State Bank... your OTP...",
  "scam_tactics_detected": ["OTP request", "Urgency pressure", "Bank impersonation"],
  "deepfake_voice_indicators": ["robotic cadence", "unnatural pauses"],
  "user_advice": "Disconnect immediately. Real bank officials never ask for OTP."
}
```

### Simulate Bank Freeze

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"account_alias":"Primary Bank Account (XXXX1234)","reason":"OTP request detected","duration_minutes":15}' \
  http://localhost:8000/api/simulate-freeze
```

Response:
```json
{
  "status": "SIMULATED_FREEZE_ACTIVE",
  "disclaimer": "Demo simulation only — third-party apps cannot directly freeze live bank accounts.",
  "account_alias": "Primary Bank Account (XXXX1234)",
  "freeze_duration_minutes": 15,
  "helpline_1930": "1930",
  "next_steps": [
    "Open your official bank or UPI app immediately and lock your debit/credit card.",
    "Change your UPI PIN, net-banking password, and MPIN right away.",
    "Call 1930 or visit cybercrime.gov.in if money was debited."
  ]
}
```

## Multi-Page Web Design

The web interface follows a multi-page architecture matching your live Netlify site:

| Page | Path | Description |
|------|------|-------------|
| Home (Landing) | `/` | Purple gradient welcome page with hero section, features, stats, and CTAs |
| Home (Dashboard) | `/dashboard` | Full command center with real-time call monitoring |
| Login/Auth | `/login` | Sign In / Create Account tabs with persistent localStorage session |
| Analysis | `/analysis` | Audio upload interface with mock scenarios and results display |
| Protection | `/protection` | Emergency panel with freeze button and Cyber Helpline 1930 |

### Authentication Flow

The login page uses `localStorage` for session persistence:

```javascript
// Save user session
localStorage.setItem('swaraguard_user', JSON.stringify({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+91 98765 43210',
  guardianContact: '+91 91234 56789'
}));

// Read user session
const user = JSON.parse(localStorage.getItem('swaraguard_user'));
```

## Mock Bank API

Located in `mock-bank-api/` (separate FastAPI service on port 8001):

### Pre-seeded Accounts

| Account ID | Owner | Type | Balance |
|------------|-------|------|---------|
| `ACC-IND-1001` | Saradhi Yelagonda | Savings | ₹75,000.00 |
| `ACC-IND-1002` | Acme Retail Tech Pvt Ltd | Current | ₹2,500,000.00 |
| `ACC-IND-1003` | Cyber Safe Emergency Reserve | Savings | ₹100,000.00 |

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/accounts` | POST | Create new account |
| `/api/accounts/{id}` | GET | Get account balance |
| `/api/accounts/{id}/statement` | GET | Get transaction history |
| `/api/accounts/{id}/freeze` | POST | Freeze account |
| `/api/accounts/{id}/unfreeze` | POST | Unfreeze account |
| `/api/transfers` | POST | Atomic transfer with idempotency |

**Note**: All amounts stored as integer paise to avoid floating-point precision issues.

## Features

### Real-time Analysis
- 3-5 second audio chunks analyzed continuously
- Gemini AI detects deepfake voices, scam intent, and credential requests
- Multilingual support: Hindi, Telugu, English

### Risk Scoring
- **Low (0-39)**: Continue monitoring
- **Medium (40-69)**: Show warning notification
- **High (70-100)**: Auto-terminate call + activate protection flow

### Protection Flow
1. Simulated 24-hour bank account freeze
2. Emergency helpline (1930) integration
3. Bank app deep links
4. Pre-filled SMS templates
5. Dashboard status tracking

### Demo Mode
- Pre-recorded scam scenarios: Bank scam, Digital arrest, Safe conversation
- Instant risk assessment
- Educational indicators

## Project Structure

```
SwaraGuard/
├── backend/                 # Multi-page web dashboard
│   ├── api/                 # API modules
│   │   ├── bank_service.py  # Atomic SQLite transfers
│   │   ├── analyze_audio.py # Gemini analysis endpoint
│   │   └── main.py          # FastAPI server
│   ├── dashboard/           # Dashboard HTML/CSS/JS
│   └── tests/              # Backend tests
├── mock-bank-api/          # SQLite-based mock banking
│   ├── app.py              # FastAPI bank API
│   ├── database.py         # SQLite operations (paise math)
│   └── models.py           # Pydantic schemas
├── web-designs/            # Static multi-page designs
│   ├── page1_home.html     # Purple gradient landing
│   ├── page2_analysis.html # Audio upload interface
│   └── page3_protection.html# Emergency protection panel
├── android/               # Kotlin mobile app
│   └── app/src/main/java/com/swaraguard/app/
│       ├── ui/             # Activities
│       ├── service/        # Foreground service
│       ├── model/          # Data classes
│       └── network/        # API client
├── test_audio/
│   └── sample.m4a          # Demo audio file
├── index.html              # Web dashboard (port 8000)
├── login.html              # Authentication page
├── dashboard.html          # Legacy dashboard
├── main.py                 # Entry point
├── analyze_audio.py        # Audio analysis module
└── netlify.toml            # Deployment redirects
```

## Testing

```bash
# Run backend tests
cd "/Users/saradhi/untitled folder1/SwaraGuard"
source .venv/bin/activate
pytest -v

# Run API tests
cd mock-bank-api
python -m pytest test_api.py -v

# Run backend service tests
cd backend
python -m pytest tests/ -v
```

## Privacy & Consent

- **Zero audio storage**: All processing is ephemeral
- **No call recording**: Audio is processed in-memory only
- **5-10 minute retention**: Processing window before automatic deletion
- **User control**: Clear session management
- **Emergency ready**: 1930 helpline always accessible

See [LIMITATIONS.md](./LIMITATIONS.md) for full privacy and security details.

## Technical Notes

### Financial Math
All bank balances and transactions use integer paise (1 INR = 100 paise) via Python `Decimal`:
```python
from decimal import Decimal
balance_paise = balance * 100  # ₹75,000.00 → 7500000 paise
```

### Brand Colors
- Background: `#0b1120` (dark slate)
- Primary: `#2563eb` / `#38bdf8` (cyan/blue)
- Trust: `#10b981` (emerald)
- Warning: `#f59e0b` (amber)
- Danger: `#ef4444` (red)

### Mobile Constraints
**Android 10+**: Cannot record phone call audio directly. SwaraGuard captures from microphone in speakerphone mode with proper user consent.

### Bank Integration
Bank actions are simulated for demo. Real protection requires user action in their bank's official app.

## Deployment

### Netlify (Static)
```bash
# Files served from root
# netlify.toml handles redirects
```

### Local Development
```bash
# Start server
uvicorn main:app --reload --port 8000

# Open browser
open http://localhost:8000
```

### Docker
```bash
docker build -t swaraguard .
docker run -p 8000:8000 swaraguard
```

## Hackathon Documentation

- [HACKATHON_BUILD_GUIDE.md](./HACKATHON_BUILD_GUIDE.md) - Build timeline and commands
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Full system architecture
- [LIMITATIONS.md](./LIMITATIONS.md) - Privacy and technical constraints

## Related Files

- `main.py` - FastAPI entry point
- `analyze_audio.py` - Gemini AI audio analysis
- `backend/api/main.py` - Dashboard API server
- `login.html` - Authentication interface
- `android/` - Mobile app source code

## License

Demo project - Hackathon submission only.

---

**Team SonicSentinels**
Live Demo: https://deepfake-scam-protection.netlify.app/

For development questions or contributions, see the linked documentation files.