# 24-Hour Hackathon Build Guide

## Track: AI & Generative AI

### Hour 0-2: Foundation Setup

**Priority: Core Backend**
```
✓ Set up FastAPI project structure
✓ Configure Gemini API key in .env
✓ Create /api/analyze endpoint
✓ Create /api/simulate-freeze endpoint
✓ Test with sample audio from test_audio/
✓ Create basic HTML dashboard
```

**Files to complete:**
- `backend/full_api.py` - Complete API
- `backend/models.py` - Pydantic schemas
- `backend/risk_engine.py` - Scoring logic
- `backend/mock_banks.py` - Bank simulation
- `index.html` - Basic dashboard

### Hour 2-6: Backend Enhancement

**Priority: Risk Engine & Mock Bank**
```
✓ Implement deepfake probability scoring
✓ Add scam tactic detection keywords
✓ Create bank freeze simulation with 24h duration
✓ Add dashboard endpoints
✓ Test API with curl commands
✓ Add error handling and logging
✓ Create sample demo audio analysis
```

**Testing commands:**
```bash
# Start server
uvicorn backend.full_api:app --reload --port 8000

# Test analyze endpoint
curl -X POST -F "file=@test_audio/sample.m4a" http://localhost:8000/api/analyze

# Test freeze endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"account_alias":"Test Account"}' \
  http://localhost:8000/api/simulate-freeze
```

### Hour 6-12: Android App Structure

**Priority: Project Setup**
```
✓ Create Android project with build.gradle
✓ Set up dependencies (Retrofit, Coroutines, Material)
✓ Create AndroidManifest.xml with permissions
✓ Create main theme (dark mode)
✓ Set up network client
✓ Create data models
✓ Create basic activities
```

**Key decisions:**
- Use Material 3 for modern UI
- Retrofit for API calls
- Foreground service for background analysis
- Custom views for risk visualization

### Hour 12-16: Core Android Features

**Priority: Real-time Analysis**

1. **CallAnalysisService**:
   ```kotlin
   // Audio chunking logic
   val CHUNK_DURATION_MS = 4000L
   val SAMPLE_RATE = 44100
   
   // Foreground service notification
   // Risk callback interface
   // Stop condition (max 2 minutes)
   ```

2. **MainActivity**:
   ```kotlin
   // Permission flow
   // Risk indicator UI
   // Start/Stop analysis button
   // Navigation to Demo Mode
   ```

3. **RiskIndicatorView**:
   ```kotlin
   // Circular progress 0-100
   // Color-coded (low/medium/high)
   // Animated transitions
   ```

### Hour 16-20: UI Completion

**Priority: User Experience**

1. **MainActivity** - Home screen with analysis
2. **DemoModeActivity** - Pre-recorded audio analysis
3. **ProtectionFlowActivity** - Bank protection flow

**UI Components:**
- Risk indicator (circular 0-100 score)
- Transcript display
- Scam tactics list
- Deepfake indicators
- Emergency actions:
  - Call 1930 button
  - Open bank app
  - Send freeze SMS
  - Dashboard link

### Hour 20-22: Integration Testing

**Priority: End-to-End Flow**

1. **Test Live Analysis**:
   - Start foreground service
   - Verify audio chunking
   - Check API calls
   - Validate risk scoring

2. **Test Demo Mode**:
   - Load sample.m4a
   - Analyze and display results
   - Trigger protection flow

3. **Test Protection Flow**:
   - Simulated bank freeze
   - Call helpline
   - Bank app links
   - SMS templates

### Hour 22-24: Polish & Demo Prep

**Priority: Presentation Ready**

1. **Create Architecture Diagram** (ARCHITECTURE.md)
2. **Document Limitations** (LIMITATIONS.md)
3. **Add Error States**
4. **Create README.md** with:
   - How to run locally
   - API documentation
   - Screenshot placeholders

5. **Demo Script**:
   - "Meet SwaraGuard - your AI scam call protector"
   - "Live call analysis with real-time risk scoring"
   - "Deepfake voice detection in Hindi/English/Telugu"
   - "Simulated bank freeze protection"
   - "Emergency actions with one-tap"

## Quick Start Commands

### Backend
```bash
cd SwaraGuard
source .venv/bin/activate  # if using venv
pip install fastapi uvicorn httpx python-dotenv
uvicorn backend.full_api:app --reload --port 8000
```

### Android
```bash
cd SwaraGuard/android
./gradlew assembleDebug
# Install on device/emulator
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Test Audio
- Sample file: `SwaraGuard/test_audio/sample.m4a`
- Analysis result: POST to `http://localhost:8000/api/analyze`

## Demo Flow (2 minutes)

1. **Opening**: "SwaraGuard uses Gemini AI to detect scam calls"
2. **Live Mode**: "The service monitors calls in real-time"
3. **Demo Mode**: "Let's scan a sample scam call" → Play → Show results
4. **Risk Display**: "70% high risk - OTP request detected"
5. **Protection**: "Activate simulated bank freeze" → Show dashboard
6. **Emergency**: "Call 1930 with one tap" → Show action buttons
7. **Closing**: "Privacy-first, no storage, user control"

## Team Roles (If working in team)

| Role | Tasks |
|------|-------|
| Backend Dev | FastAPI, Gemini API, risk engine, mock bank |
| Android Dev | Foreground service, audio capture, UI, permissions |
| ML Engineer | Model research, Gemini prompt tuning, scoring weights |
| UI/UX | Design system, accessibility, demo flow, presentation |

## Submission Checklist

- [ ] Working backend with `/api/analyze` returning valid JSON
- [ ] Android APK that installs on device
- [ ] Demo audio file included
- [ ] Architecture diagram (text)
- [ ] Live demo of:
  1. Risk scoring display
  2. Protection flow activation
  3. Emergency actions (1930 dialer)
- [ ] 1-page doc with limitations and privacy notes
- [ ] README with build instructions