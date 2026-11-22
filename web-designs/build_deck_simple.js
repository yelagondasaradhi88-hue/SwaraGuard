const pptxgen = require('pptxgenjs');

const pres = new pptxgen();
const SHAPE = pptxgen.ShapeType || {};
const RECT = 'rect';
const ROUND = 'roundRect';

// ---------- helpers ----------
function addRect(slide, x, y, w, h, fill, shadow) {
  slide.addShape(RECT, { x, y, w, h, fill: { color: fill }, shadow });
}

function addRoundRect(slide, x, y, w, h, fill, shadow = true) {
  slide.addShape(ROUND, {
    x, y, w, h,
    fill: { color: fill },
    rectRadius: 0.08,
    shadow: shadow ? { type: 'outer', color: '000000', offset: 4, blur: 6, transparency: 50 } : null,
  });
}

function addText(slide, text, { x, y, w, h, size = 16, color = '1E293B', bold = false, align = 'left', fontFace = 'Calibri', lineSpacing = 1.0, spacingAfter = 6, isTextBox = true }) {
  slide.addText([{ text: text, options: {} }], {
    x, y, w, h,
    fontSize: size,
    fontFace,
    color,
    bold,
    align,
    lineSpacing,
    spaceAfter: spacingAfter,
    isTextBox,
    margin: 0,
  });
}

function addBullet(slide, items, { x, y, w, h, size = 13, color = '64748B', spacingAfter = 8 }) {
  const runs = items.map(it => ({ text: it, options: { bullet: true, breakLine: true } }));
  slide.addText(runs, { x, y, w, h, fontSize: size, fontFace: 'Calibri', color, spaceAfter: spacingAfter, isTextBox: true, margin: 0 });
}

const DARK = '0F172A';
const LIGHT = 'FFFFFF';
const CYAN = '0EA5E9';
const AMBER = 'F59E0B';
const RED = 'EF4444';
const GREEN = '22C55E';
const PALE = 'F8FAFC';
const SLATE = '64748B';
const DARKTEXT = '1E293B';

// =========================================================
// SLIDE 1 — Title
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, DARK, false);
  addRect(s, 0, 0, 0.22, 7.5, CYAN, false);

  addText(s, 'SWARAGUARD AI', { x: 0.9, y: 1.55, w: 11.5, h: 0.9, size: 54, color: LIGHT, bold: true, fontFace: 'Cambria', align: 'center' });
  addText(s, 'Anti-Scam Call Protection for Indian Phone Numbers', { x: 0.9, y: 2.6, w: 11.5, h: 0.55, size: 20, color: '94A3B8', align: 'center' });

  const cy = 3.55;
  addRoundRect(s, 1.45, cy, 3.35, 1.35, PALE, false);
  addText(s, '40% + 40% + 20%', { x: 1.45, y: cy + 0.18, w: 3.35, h: 0.9, size: 30, color: CYAN, bold: true, align: 'center' });
  addText(s, 'Voice · Device · Transaction', { x: 1.45, y: cy + 0.92, w: 3.35, h: 0.3, size: 11, color: SLATE, align: 'center' });

  addRoundRect(s, 5.0, cy, 3.35, 1.35, PALE, false);
  addText(s, '< 5s', { x: 5.0, y: cy + 0.18, w: 3.35, h: 0.9, size: 30, color: RED, bold: true, align: 'center' });
  addText(s, 'Auto-disconnect', { x: 5.0, y: cy + 0.92, w: 3.35, h: 0.3, size: 11, color: SLATE, align: 'center' });

  addRoundRect(s, 8.55, cy, 3.35, 1.35, PALE, false);
  addText(s, '1930', { x: 8.55, y: cy + 0.18, w: 3.35, h: 0.9, size: 30, color: AMBER, bold: true, align: 'center' });
  addText(s, 'Cyber Crime Helpline', { x: 8.55, y: cy + 0.92, w: 3.35, h: 0.3, size: 11, color: SLATE, align: 'center' });

  addText(s, 'Hackathon-Ready  ·  FastAPI Backend  ·  Android App  ·  Gemini AI', { x: 0.9, y: 5.35, w: 11.5, h: 0.7, size: 14, color: SLATE, align: 'center' });
  addText(s, 'SwaraGuard AI — Built for the Hackathon', { x: 0.9, y: 6.95, w: 11.5, h: 0.35, size: 11, color: SLATE, align: 'center' });
}

// =========================================================
// SLIDE 2 — Problem
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, DARK, false);

  addText(s, 'The Problem', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'Why Indian phone users need scam protection', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: '94A3B8' });

  addText(s, 'Phone scams target millions across India every day.', { x: 0.6, y: 1.5, w: 7.6, h: 0.4, size: 18, color: DARK, bold: true });

  addBullet(s, [
    'Bank scams — fake KYC, OTP, UPI fraud calls',
    'Digital Arrest threats — impersonating police/CBI',
    'Telugu / Hinglish / English scam scripts in regional languages',
    'Unknown numbers can’t be trusted — but normal unknown calls are safe',
    'Victims lose savings before they can react or block the caller',
  ], { x: 0.6, y: 2.05, w: 7.55, h: 3.6, size: 15.5, color: SLATE });

  addRoundRect(s, 8.5, 1.7, 4.25, 4.1, PALE, true);
  addText(s, 'Real Impact', { x: 8.85, y: 2.0, w: 3.6, h: 0.4, size: 17, color: RED, bold: true });
  addText(s, '₹ thousands lost per victim on average', { x: 8.85, y: 2.5, w: 3.6, h: 0.4, size: 14, color: SLATE });
  addText(s, 'Minutes to react before money is drained', { x: 8.85, y: 3.0, w: 3.6, h: 0.4, size: 13.5, color: SLATE });
  addText(s, 'No real-time defense exists on the phone today', { x: 8.85, y: 3.55, w: 3.6, h: 0.4, size: 13.5, color: SLATE });

  addRoundRect(s, 0.6, 6.05, 12.13, 0.9, RED, false);
  addText(s, 'SwaraGuard detects scams in real time and disconnects high-risk calls before damage is done.', { x: 0.9, y: 6.22, w: 11.55, h: 0.6, size: 14, color: LIGHT, bold: true, align: 'center' });
}

// =========================================================
// SLIDE 3 — Solution
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, CYAN, false);

  addText(s, 'The Solution', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'How SwaraGuard stops scam calls', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'BAE6FD' });

  const steps = [
    { num: '1', title: 'Incoming Call', desc: 'CallScreeningService listens for the call and reads the caller number.', color: CYAN },
    { num: '2', title: 'AI Analysis', desc: 'Audio is sent to the FastAPI backend; Gemini scores scam risk (0–100).', color: AMBER },
    { num: '3', title: 'Risk Decision', desc: '< 60 = ALLOW   60–79 = WARN   ≥ 80 = DISCONNECT + ALERT.', color: GREEN },
    { num: '4', title: 'Protect User', desc: 'Guardian alert, 1930 helpline card, optional 15-minute account freeze.', color: RED },
  ];
  let sx = 0.6;
  steps.forEach(st => {
    addRoundRect(s, sx, 1.6, 2.93, 3.35, PALE, true);
    addRoundRect(s, sx + 1.06, 1.72, 0.8, 0.8, st.color, false);
    addText(s, st.num, { x: sx + 1.06, y: 1.82, w: 0.8, h: 0.62, size: 22, color: LIGHT, bold: true, align: 'center' });
    addText(s, st.title, { x: sx + 0.2, y: 2.72, w: 2.53, h: 0.4, size: 14.5, color: DARKTEXT, bold: true, align: 'center' });
    addText(s, st.desc, { x: sx + 0.2, y: 3.25, w: 2.53, h: 1.55, size: 11.5, color: SLATE, align: 'center', lineSpacing: 1.15 });
    sx += 3.1;
  });

  addRoundRect(s, 0.6, 5.3, 12.13, 1.65, DARK, true);
  addText(s, 'One Rule That Matters', { x: 0.95, y: 5.5, w: 11.5, h: 0.4, size: 16, color: CYAN, bold: true });
  addText(s, 'Unknown number + NORMAL speech = SAFE   |   Unknown number + SCAM speech = HIGH RISK + Auto-Disconnect', { x: 0.95, y: 5.98, w: 11.5, h: 0.6, size: 14, color: LIGHT, align: 'center', lineSpacing: 1.15 });
}

// =========================================================
// SLIDE 4 — Features
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, GREEN, false);

  addText(s, 'Key Features', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'Everything the app does to keep callers safe', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'BBF7D0' });

  const feats = [
    { t: 'Unknown Number Toggle', d: 'Demo switch shows how unknown + normal = SAFE, unknown + scam = HIGH RISK.', c: CYAN },
    { t: 'Risk Score (0–100)', d: 'Voice, device & transaction risk combined — weighted 40/40/20.', c: AMBER },
    { t: 'Auto-Disconnect', d: 'High-risk calls (≥80) disconnect with a 5-second countdown banner.', c: RED },
    { t: 'Guardian Alert', d: 'Notifies a trusted contact when a scam is detected.', c: CYAN },
    { t: 'Freeze Account (15 min)', d: 'Simulated bank account lock with countdown timer.', c: AMBER },
    { t: '1930 Helpline Card', d: 'One-tap call to the Indian Cyber Crime Helpline.', c: GREEN },
  ];
  let x = 0.6, y = 1.6;
  feats.forEach((f, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const cx = 0.6 + col * 4.14;
    const cy = 1.6 + row * 2.5;
    addRoundRect(s, cx, cy, 3.9, 2.25, PALE, true);
    addRoundRect(s, cx + 0.18, cy + 0.18, 0.5, 0.5, f.c, false);
    addText(s, f.t, { x: cx + 0.85, y: cy + 0.16, w: 2.9, h: 0.45, size: 14.5, color: DARKTEXT, bold: true });
    addText(s, f.d, { x: cx + 0.22, y: cy + 0.72, w: 3.45, h: 1.4, size: 11.5, color: SLATE, lineSpacing: 1.12 });
  });
}

// =========================================================
// SLIDE 5 — Risk Engine
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, AMBER, false);

  addText(s, 'Unified Risk Engine', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 32, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'Voice + Device + Transaction = one trustworthy score', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'FDE68A' });

  const cols = [
    { t: 'Voice Risk (40%)', c: CYAN, items: ['Deepfake / TTS voice traits', 'Scam tactics detected', 'Voice risk score from Gemini'] },
    { t: 'Device Risk (40%)', c: AMBER, items: ['Unknown caller flag', 'SIM / device events', 'Call-pattern anomalies'] },
    { t: 'Transaction Risk (20%)', c: GREEN, items: ['Account locked flag', 'High transaction count', 'Large transfer amounts'] },
  ];
  let cx = 0.6;
  cols.forEach(c => {
    addRoundRect(s, cx, 1.6, 3.95, 3.3, PALE, true);
    addRoundRect(s, cx + 1.37, 1.72, 1.2, 0.5, c.c, false);
    addText(s, c.t, { x: cx + 0.25, y: 1.76, w: 3.45, h: 0.45, size: 15, color: c.c, bold: true, align: 'center' });
    addBullet(s, c.items, { x: cx + 0.25, y: 2.5, w: 3.45, h: 2.2, size: 12.5, color: SLATE });
    cx += 4.13;
  });

  addRoundRect(s, 0.6, 5.15, 12.13, 1.75, DARK, true);
  addText(s, 'Score → Action', { x: 0.95, y: 5.32, w: 11.5, h: 0.4, size: 15, color: CYAN, bold: true });
  addText(s, 'LOW (<30) → MONITOR / ALLOW    MEDIUM (30–59) → WARN    HIGH (60–79) → WARN + PROTECT    CRITICAL (≥80) → DISCONNECT + ALERT', { x: 0.95, y: 5.82, w: 11.5, h: 0.95, size: 13.5, color: LIGHT, align: 'center', lineSpacing: 1.4 });
}

// =========================================================
// SLIDE 6 — Demo Dashboard
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, DARK, false);

  addText(s, 'Demo Dashboard', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 32, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'Colorful security command center you can try right now', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'CBD5E1' });

  const dash = [
    { t: 'Risk Ring', d: 'Live 0–100 risk score with color-coded level (LOW / MEDIUM / HIGH / CRITICAL).' },
    { t: 'Scenario Buttons', d: 'One-click demos: Family Call, Bank Scam, Digital Arrest, Telugu Scam.' },
    { t: 'Freeze Countdown', d: '15-minute simulated account lock with live timer.' },
    { t: 'Guardian Actions', d: 'Approve unfreeze or keep account frozen after an alert.' },
    { t: 'Audit Log', d: 'Timestamped trail of every analysis and action taken.' },
    { t: '1930 Helpline', d: 'One-tap call to the Indian Cyber Crime Helpline.' },
  ];
  let dy = 1.55;
  dash.forEach((d, i) => {
    const row = i % 3;
    const col = Math.floor(i / 3);
    const cx = 0.6 + col * 6.05;
    const cy = dy + row * 1.78;
    addRoundRect(s, cx, cy, 5.75, 1.6, PALE, true);
    addRoundRect(s, cx + 0.2, cy + 0.22, 0.42, 0.42, i % 2 === 0 ? CYAN : AMBER, false);
    addText(s, d.t, { x: cx + 0.8, y: cy + 0.16, w: 4.7, h: 0.4, size: 14, color: DARKTEXT, bold: true });
    addText(s, d.d, { x: cx + 0.22, y: cy + 0.68, w: 5.3, h: 0.85, size: 11.5, color: SLATE, lineSpacing: 1.1 });
  });

  addText(s, 'Open: http://localhost:8000/dashboard   ·   Backend: python -m backend.api.main', { x: 0.6, y: 6.95, w: 12, h: 0.35, size: 11, color: SLATE, align: 'center' });
}

// =========================================================
// SLIDE 7 — Android Architecture
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, RED, false);

  addText(s, 'Android Phase 2', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 32, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'Real-time call monitoring & auto-disconnect on-device', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'FECACA' });

  const android = [
    { t: 'CallScreeningService', d: 'Listens for INCOMING_CALL → queries backend API → risk score → ALLOW / WARN / DISCONNECT.', c: CYAN },
    { t: 'InCallService (Foreground)', d: 'Live audio capture, real-time transcription, risk overlay, emergency buttons.', c: AMBER },
    { t: 'DisconnectCountdown', d: '5-second full-screen emergency UI → auto-disconnect → show 1930 helpline.', c: RED },
  ];
  let ax = 0.6;
  android.forEach(a => {
    addRoundRect(s, ax, 1.6, 3.95, 3.5, PALE, true);
    addRoundRect(s, ax + 1.37, 1.72, 1.2, 0.5, a.c, false);
    addText(s, a.t, { x: ax + 0.25, y: 1.76, w: 3.45, h: 0.5, size: 14.5, color: a.c, bold: true, align: 'center' });
    addText(s, a.d, { x: ax + 0.22, y: 2.5, w: 3.5, h: 2.4, size: 12, color: SLATE, lineSpacing: 1.15 });
    ax += 4.13;
  });

  addText(s, 'Permissions: RECORD_AUDIO, READ_PHONE_STATE, FOREGROUND_SERVICE, INTERNET, DISCONNECT_PHONE_STATE', { x: 0.6, y: 5.35, w: 12, h: 0.45, size: 12, color: SLATE });
  addRoundRect(s, 0.6, 5.9, 12.13, 1.0, DARK, false);
  addText(s, 'Fallback: AccessibilityService simulates END_CALL when system telephony permission is unavailable.', { x: 0.95, y: 6.05, w: 11.5, h: 0.7, size: 12.5, color: LIGHT, align: 'center', lineSpacing: 1.15 });
}

// =========================================================
// SLIDE 8 — Tech Stack & Roadmap
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, LIGHT, false);
  addRect(s, 0, 0, 13.333, 1.15, '334155', false);

  addText(s, 'Tech Stack & Roadmap', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 32, color: LIGHT, bold: true, fontFace: 'Cambria' });
  addText(s, 'What we built and where we go next', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'CBD5E1' });

  addRoundRect(s, 0.6, 1.55, 5.9, 4.2, PALE, true);
  addText(s, 'Tech Stack', { x: 0.95, y: 1.82, w: 5.2, h: 0.4, size: 17, color: DARKTEXT, bold: true });
  addBullet(s, [
    'FastAPI + Uvicorn (Python backend)',
    'Gemini API (google-genai SDK)',
    'Pydantic v2 (structured JSON output)',
    'Kotlin / Android (CallScreeningService, InCallService)',
    'HTML / CSS / JS (colorful dashboard)',
    'python-dotenv, httpx, pytest',
  ], { x: 0.95, y: 2.32, w: 5.25, h: 3.3, size: 13, color: SLATE });

  addRoundRect(s, 6.8, 1.55, 5.93, 4.2, DARK, true);
  addText(s, 'Roadmap', { x: 7.15, y: 1.82, w: 5.2, h: 0.4, size: 17, color: CYAN, bold: true });
  const road = [
    { t: 'Now', d: 'Demo backend + dashboard + Android docs', c: AMBER },
    { t: 'Next', d: 'Gemini live transcription + ONNX deepfake model', c: CYAN },
    { t: 'Later', d: 'Local encrypted storage + real 1930 integration', c: GREEN },
  ];
  let ry = 2.4;
  road.forEach(r => {
    addRoundRect(s, 7.15, ry, 0.5, 0.5, r.c, false);
    addText(s, r.t, { x: 7.15, y: ry + 0.08, w: 0.5, h: 0.36, size: 12, color: LIGHT, bold: true, align: 'center' });
    addText(s, r.d, { x: 7.85, y: ry, w: 4.6, h: 0.6, size: 12, color: 'E2E8F0', lineSpacing: 1.1 });
    ry += 0.78;
  });

  addRoundRect(s, 0.6, 6.0, 12.13, 0.95, GREEN, false);
  addText(s, 'Hackathon-ready demo: run `python -m backend.api.main` and open `http://localhost:8000/dashboard`', { x: 0.95, y: 6.15, w: 11.5, h: 0.7, size: 13.5, color: LIGHT, align: 'center', lineSpacing: 1.2 });
}

// =========================================================
// SLIDE 9 — Thank You
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, 0, 0, 13.333, 7.5, DARK, false);
  addRect(s, 0, 0, 0.22, 7.5, CYAN, false);

  addText(s, 'Thank You', { x: 0.9, y: 2.3, w: 11.5, h: 0.7, size: 48, color: LIGHT, bold: true, fontFace: 'Cambria', align: 'center' });
  addText(s, 'SwaraGuard AI — Anti-Scam Call Protection', { x: 0.9, y: 3.15, w: 11.5, h: 0.45, size: 18, color: '94A3B8', align: 'center' });
  addText(s, 'Built for the Hackathon  ·  FastAPI  ·  Gemini AI  ·  Android', { x: 0.9, y: 3.7, w: 11.5, h: 0.4, size: 14, color: SLATE, align: 'center' });
  addText(s, 'Try it:  python -m backend.api.main  →  http://localhost:8000/dashboard', { x: 0.9, y: 4.7, w: 11.5, h: 0.45, size: 15, color: CYAN, bold: true, align: 'center' });
  addText(s, 'Questions?  SwaraGuard AI Team', { x: 0.9, y: 6.6, w: 11.5, h: 0.35, size: 11, color: SLATE, align: 'center' });
}

pres.writeFile({ fileName: 'SwaraGuard_Hackathon_Deck.pptx' }).then(() => {
  console.log('Deck written: SwaraGuard_Hackathon_Deck.pptx');
});
