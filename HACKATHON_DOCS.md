# SwaraGuard Hackathon Documentation

## Live Demo
Visit https://deepfake-scam-protection.netlify.app/ to see the running demo.

## Project Overview
Fraudsters increasingly use AI voice cloning and real-time voice translation from unknown numbers to imitate a victim's own family members—alongside fake bank or authority scripts—to create panic and steal OTPs, UPI PINs, or money. However, blindly blocking all unknown numbers fails in real life because a genuine family member may call from a new mobile number and must never be blocked. SwaraGuard solves this by analyzing what happens inside the call—keeping genuine calls from a family member's new number completely SAFE with zero blocking, while detecting synthetic/AI-cloned voice cues, suspicious scam intent, and credential requests to flag fraud, guide users with a simulated account hold and 1930 helpline workflow, and move toward auto-disconnect in our next mobile build.

SwaraGuard is an Android anti-scam app that uses AI to detect and prevent phone call fraud in real-time. It analyzes live calls for scam indicators and can automatically terminate high-risk calls.

## Key Features
- **Real-time Analysis**: 3-5 second audio chunks analyzed continuously for up to 2 minutes
- **Deepfake Voice Detection**: Identifies synthetic/TTS voices using Gemini AI
- **Scam Intent Detection**: Multilingual (Hindi, Telugu, English) detection of OTP requests, UPI pressure, digital arrest threats
- **Risk Engine**: Combined scoring from voice analysis and scam tactics (40% voice + 40% device + 20% transaction)
- **Protection Flow**: Simulated bank freeze with emergency actions and 15-minute countdown
- **Demo Mode**: Analyze pre-recorded scam audio files

## How to Run
### Backend
```bash
# Install dependencies
pip install fastapi uvicorn httpx python-dotenv

# Configure API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run server
uvicorn backend.full_api:app --reload --port 8000
```

### Android
```bash
# Open Android Studio and import:
# File → Open → SwaraGuard/android

# Or build via CLI
cd SwaraGuard/android
./gradlew assembleDebug
```

### Dashboard
Open http://localhost:8000/dashboard in your browser to access the colorful UI with risk ring, scenario buttons, countdown timer, and guardian alerts.

## Demo Scenarios
- **Family Call**: Low risk (~15%) → Allow call
- **Bank Scam**: High risk (~85%) → 5-second countdown → Auto-disconnect
- **Digital Arrest**: High risk (~90%) → 5-second countdown → Auto-disconnect
- **Telugu Scam**: High risk (~88%) → 5-second countdown → Auto-disconnect

## Presentation
- Use the 9-slide PPTX deck (`web-designs/SwaraGuard_Hackathon_Deck.pptx`) for your hackathon pitch.
- Include live demo screenshots and explain the risk scoring system.

## Contact
SwaraGuard AI Team  
Email: team@swaraguard.example  
GitHub: https://github.com/your-repo/swaraguard