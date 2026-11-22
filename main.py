import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from analyze_audio import analyze_audio_file
except (ImportError, ValueError):
    try:
        from .analyze_audio import analyze_audio_file
    except (ImportError, ValueError):
        analyze_audio_file = None

app = FastAPI(title="SwaraGuard")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DESIGNS_DIR = os.path.join(BASE_DIR, "web-designs")
LOGIN_PATH = os.path.join(WEB_DESIGNS_DIR, "login.html")
DASHBOARD_PATH = os.path.join(WEB_DESIGNS_DIR, "page1_home.html")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(WEB_DESIGNS_DIR, "page1_home.html"))

@app.get("/login")
@app.get("/login.html")
def serve_login():
    return FileResponse(LOGIN_PATH)

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(DASHBOARD_PATH)

@app.get("/analysis")
@app.get("/page2_analysis.html")
def serve_analysis():
    return FileResponse(os.path.join(WEB_DESIGNS_DIR, "page2_analysis.html"))

@app.get("/protection")
@app.get("/page3_protection.html")
def serve_protection():
    return FileResponse(os.path.join(WEB_DESIGNS_DIR, "page3_protection.html"))

@app.get("/live-call")
@app.get("/live-call.html")
def serve_live_call():
    return FileResponse(os.path.join(WEB_DESIGNS_DIR, "live_call_guard.html"))

@app.post("/api/analyze")
async def analyze_uploaded_audio(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "audio.m4a")[1] or ".m4a"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name
        return analyze_audio_file(temp_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
class FreezeRequest(BaseModel):
    account_alias: str = "Primary Bank Account (XXXX1234)"
    reason: str = "Possible OTP / credential exposure during scam call"
    duration_minutes: int = 15


@app.post("/api/simulate-freeze")
def simulate_bank_freeze(req: FreezeRequest):
    freeze_until = datetime.now(timezone.utc) + timedelta(minutes=req.duration_minutes)
    return {
        "status": "SIMULATED_FREEZE_ACTIVE",
        "disclaimer": "Demo simulation only — third-party apps cannot directly freeze live bank accounts.",
        "account_alias": req.account_alias,
        "reason": req.reason,
        "freeze_duration_minutes": req.duration_minutes,
        "locked_until_utc": freeze_until.isoformat(),
        "helpline_1930": "1930",
        "next_steps": [
            "Open your official bank or UPI app immediately and lock your debit/credit card.",
            "Change your UPI PIN, net-banking password, and MPIN right away.",
            "Call 1930 or visit cybercrime.gov.in if money was debited.",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SwaraGuard on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
