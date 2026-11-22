const pptxgen = require('pptxgenjs');

const pres = new pptxgen();
pres.layout = pptxgen.LAYOUT_16x9;

// ---------- Theme ----------
const THEME = {
  name: 'SwaraGuard',
  headFontFace: 'Cambria',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '0F172A',   // deep navy (dark bg)
    lt1: 'FFFFFF',   // white (light bg)
    dk2: '1E293B',   // slate dark
    lt2: 'F1F5F9',   // light slate
    accent1: '0EA5E9', // cyan
    accent2: 'F59E0B', // amber
    accent3: 'EF4444', // red / danger
    accent4: '22C55E', // green / safe
    hlink: '38BDF8',
    folHlink: '7DD3FC',
  },
};
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

const C = pres.SchemeColor; // not used directly; we use hex for scheme colors

const DARK = THEME.colors.dk1;
const LIGHT = THEME.colors.lt1;
const SLATE = THEME.colors.dk2;
const PALE = THEME.colors.lt2;
const CYAN = THEME.colors.accent1;
const AMBER = THEME.colors.accent2;
const RED = THEME.colors.accent3;
const GREEN = THEME.colors.accent4;

// ---------- helpers ----------
function addRect(slide, { x, y, w, h, fill, line, shadow = false }) {
  const o = { x, y, w, h, fill: { color: fill }, line: line ? { color: line.color, width: line.width || 1 } : null };
  if (shadow) o.shadow = { type: 'outer', color: '000000', offset: 6, blur: 8, transparency: 45 };
  slide.addShape(pptxgen.ShapeType.rect, o);
}

function addRoundRect(slide, { x, y, w, h, fill, line, shadow = true, radius = 0.08 }) {
  const o = {
    x, y, w, h,
    fill: { color: fill },
    rectRadius: radius,
    line: line ? { color: line.color, width: line.width || 1 } : null,
  };
  if (shadow) o.shadow = { type: 'outer', color: '000000', offset: 4, blur: 6, transparency: 50 };
  slide.addShape(pptxgen.ShapeType.roundedRectangle, o);
}

function addText(slide, text, { x, y, w, h, size = 16, color = SLATE, bold = false, align = 'left', fontFace = THEME.bodyFontFace, lineSpacing = 1.0, spacingAfter = 6, bullet = false, isTextBox = true }) {
  const items = Array.isArray(text) ? text : [text];
  const runs = items.map(t => {
    if (typeof t === 'string') return { text: t, options: {} };
    return t;
  });
  slide.addText(runs, {
    x, y, w, h,
    fontSize: size,
    fontFace,
    color,
    bold,
    align,
    lineSpacing,
    spaceAfter: spacingAfter,
    bullet,
    isTextBox,
    margin: 0,
  });
}

function addBullet(slide, items, { x, y, w, h, size = 16, color = SLATE, fontFace = THEME.bodyFontFace, spaceAfter = 10 }) {
  const runs = items.map(it => {
    if (typeof it === 'string') return { text: it, options: { bullet: true, breakLine: true } };
    return { ...it, options: { ...it.options, bullet: true, breakLine: true } };
  });
  slide.addText(runs, { x, y, w, h, fontSize: size, fontFace, color, spaceAfter, isTextBox: true, margin: 0 });
}

function statCard(slide, x, y, w, h, number, label, color, sub) {
  addRoundRect(slide, { x, y, w, h, fill: LIGHT, line: { color: color, width: 1 }, shadow: true });
  addText(slide, number, { x: x + 0.25, y: y + 0.18, w: w - 0.5, h: 0.55, size: 30, color, bold: true, align: 'center' });
  addText(slide, label, { x: x + 0.25, y: y + 0.82, w: w - 0.5, h: 0.4, size: 12.5, color: SLATE, bold: true, align: 'center' });
  if (sub) {
    addText(slide, sub, { x: x + 0.25, y: y + 1.25, w: w - 0.5, h: 0.3, size: 10.5, color: '64748B', align: 'center' });
  }
}

function chip(slide, x, y, text, fill, color = LIGHT, size = 11) {
  const w = text.length * 0.075 + 0.5;
  addRoundRect(slide, { x, y, w, h: 0.34, fill, shadow: false, radius: 0.5 });
  addText(slide, text, { x, y: y + 0.05, w, h: 0.26, size, color, bold: true, align: 'center' });
  return w;
}

// =========================================================
// SLIDE 1 — Title (dark)
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: DARK });
  // accent band
  addRect(s, { x: 0, y: 0, w: 0.22, h: 7.5, fill: CYAN });

  addText(s, 'SWARAGUARD AI', { x: 0.9, y: 1.55, w: 11.5, h: 0.9, size: 54, color: LIGHT, bold: true, fontFace: THEME.headFontFace, align: 'center' });
  addText(s, 'Anti-Scam Call Protection for Indian Phone Numbers', { x: 0.9, y: 2.6, w: 11.5, h: 0.55, size: 20, color: '94A3B8', align: 'center' });

  // three stat chips
  const cy = 3.55;
  statCard(s, 1.45, cy, 3.35, 1.35, '40% + 40% + 20%', 'Voice · Device · Transaction', CYAN);
  statCard(s, 5.0, cy, 3.35, 1.35, '< 5s', 'Auto-disconnect', RED);
  statCard(s, 8.55, cy, 3.35, 1.35, '1930', 'Cyber Crime Helpline', AMBER);

  addText(s, [
    { text: 'Hackathon-Ready  ·  FastAPI Backend  ·  Android App  ·  Gemini AI', options: { bold: true } },
    { text: 'Real-time scam detection · Auto-call disconnect · Guardian alerts · Bank account freeze simulation', options: {} },
  ], { x: 0.9, y: 5.35, w: 11.53, h: 1.1, size: 14, color: 'CBD5E1', align: 'center', lineSpacing: 1.2 });

  addText(s, 'SwaraGuard AI — Built for the Hackathon', { x: 0.9, y: 6.95, w: 11.5, h: 0.35, size: 11, color: '64748B', align: 'center' });
}

// =========================================================
// SLIDE 2 — The Problem
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: DARK });
  addText(s, 'The Problem', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'Why Indian phone users need scam protection', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: '94A3B8' });

  addText(s, 'Phone scams target millions across India every day.', { x: 0.6, y: 1.5, w: 7.6, h: 0.4, size: 18, color: DARK, bold: true });

  addBullet(s, [
    { text: 'Bank scams — fake KYC, OTP, UPI fraud calls', options: {} },
    { text: 'Digital Arrest threats — impersonating police/CBI', options: {} },
    { text: 'Telugu / Hinglish / English scam scripts in regional languages', options: {} },
    { text: 'Unknown numbers can’t be trusted — but normal unknown calls are safe', options: {} },
    { text: 'Victims lose savings before they can react or block the caller', options: {} },
  ], { x: 0.6, y: 2.05, w: 7.55, h: 3.6, size: 15.5, color: SLATE, spaceAfter: 12 });

  // right card: the cost
  addRoundRect(s, { x: 8.5, y: 1.7, w: 4.25, h: 4.1, fill: 'F8FAFC', line: { color: 'E2E8F0', width: 1 }, shadow: true });
  addText(s, 'Real Impact', { x: 8.85, y: 2.0, w: 3.6, h: 0.4, size: 17, color: RED, bold: true });
  addText(s, [
    { text: '₹ thousands ', options: { bold: true, color: RED } },
    { text: 'lost per victim on average', options: {} },
  ], { x: 8.85, y: 2.5, w: 3.6, h: 0.4, size: 14, color: SLATE });
  addText(s, 'Minutes to react before money is drained', { x: 8.85, y: 3.0, w: 3.6, h: 0.4, size: 13.5, color: SLATE });
  addText(s, [
    { text: 'No real-time defense ', options: { bold: true, color: RED } },
    { text: 'exists on the phone today', options: {} },
  ], { x: 8.85, y: 3.55, w: 3.6, h: 0.4, size: 13.5, color: SLATE });

  // bottom rule bar
  addRoundRect(s, { x: 0.6, y: 6.05, w: 12.13, h: 0.9, fill: RED, shadow: false });
  addText(s, [
    { text: 'SwaraGuard detects scams in real time and disconnects high-risk calls before damage is done.', options: { color: LIGHT, bold: true } },
  ], { x: 0.9, y: 6.22, w: 11.55, h: 0.6, size: 14, color: LIGHT, align: 'center' });
}

// =========================================================
// SLIDE 3 — The Solution
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: CYAN });
  addText(s, 'The Solution', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'How SwaraGuard stops scam calls', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'BAE6FD' });

  const steps = [
    { num: '1', title: 'Incoming Call', desc: 'CallScreeningService listens for the call and reads the caller number.', color: CYAN },
    { num: '2', title: 'AI Analysis', desc: 'Audio is sent to the FastAPI backend; Gemini scores scam risk (0–100).', color: AMBER },
    { num: '3', title: 'Risk Decision', desc: '< 60 = ALLOW   60–79 = WARN   ≥ 80 = DISCONNECT + ALERT.', color: GREEN },
    { num: '4', title: 'Protect User', desc: 'Guardian alert, 1930 helpline card, optional 15-minute account freeze.', color: RED },
  ];
  let sx = 0.6;
  steps.forEach(st => {
    addRoundRect(s, { x: sx, y: 1.6, w: 2.93, h: 3.35, fill: 'F8FAFC', line: { color: st.color, width: 2 }, shadow: true });
    addRoundRect(s, { x: sx + 1.06, y: 1.72, w: 0.8, h: 0.8, fill: st.color, shadow: false, radius: 0.2 });
    addText(s, st.num, { x: sx + 1.06, y: 1.82, w: 0.8, h: 0.62, size: 22, color: LIGHT, bold: true, align: 'center' });
    addText(s, st.title, { x: sx + 0.2, y: 2.72, w: 2.53, h: 0.4, size: 14.5, color: DARK, bold: true, align: 'center' });
    addText(s, st.desc, { x: sx + 0.2, y: 3.25, w: 2.53, h: 1.55, size: 11.5, color: SLATE, align: 'center', lineSpacing: 1.15 });
    sx += 3.1;
  });

  addRoundRect(s, { x: 0.6, y: 5.3, w: 12.13, h: 1.65, fill: DARK, shadow: true });
  addText(s, 'One Rule That Matters', { x: 0.95, y: 5.5, w: 11.5, h: 0.4, size: 16, color: CYAN, bold: true });
  addText(s, 'Unknown number + NORMAL speech = SAFE   |   Unknown number + SCAM speech = HIGH RISK + Auto-Disconnect', { x: 0.95, y: 5.98, w: 11.5, h: 0.6, size: 14, color: LIGHT, align: 'center', lineSpacing: 1.15 });
}

// =========================================================
// SLIDE 4 — Key Features
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: GREEN });
  addText(s, 'Key Features', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'Everything the app does to keep callers safe', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'BBF7D0' });

  const feats = [
    { t: 'Unknown Number Toggle', d: 'Demo switch shows how unknown + normal = SAFE, unknown + scam = HIGH RISK.', c: CYAN },
    { t: 'Risk Score (0–100)', d: 'Voice, device & transaction risk combined — weighted 40/40/20.', c: AMBER },
    { t: 'Auto-Disconnect', d: 'High-risk calls (≥80) disconnect with a 5-second countdown banner.', c: RED },
    { t: 'Guardian Alert', d: 'Notifies a trusted contact when a scam is detected.', c: CYAN },
    { t: 'Freeze Account (15 min)', d: 'Simulated bank account lock with countdown timer.', c: AMBER },
    { t: '1930 Helpline Card', d: 'One-tap access to the Indian Cyber Crime Helpline.', c: GREEN },
  ];
  let fx = 0.6, fy = 1.6;
  feats.forEach((f, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.6 + col * 4.14;
    const y = 1.6 + row * 2.5;
    addRoundRect(s, { x, y, w: 3.9, h: 2.25, fill: 'F8FAFC', line: { color: f.c, width: 1 }, shadow: true });
    addRoundRect(s, { x: x + 0.18, y: y + 0.18, w: 0.5, h: 0.5, fill: f.c, shadow: false, radius: 0.2 });
    addText(s, f.t, { x: x + 0.85, y: y + 0.16, w: 2.9, h: 0.45, size: 14.5, color: DARK, bold: true });
    addText(s, f.d, { x: x + 0.22, y: y + 0.72, w: 3.45, h: 1.4, size: 11.5, color: SLATE, lineSpacing: 1.12 });
  });
}

// =========================================================
// SLIDE 5 — Risk Engine
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: AMBER });
  addText(s, 'Unified Risk Engine', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'Voice + Device + Transaction = one trustworthy score', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'FDE68A' });

  const cols = [
    { t: 'Voice Risk (40%)', c: CYAN, items: ['Deepfake / TTS voice traits', 'Scam tactics detected', 'Voice risk score from Gemini'] },
    { t: 'Device Risk (40%)', c: AMBER, items: ['Unknown caller flag', 'SIM / device events', 'Call-pattern anomalies'] },
    { t: 'Transaction Risk (20%)', c: GREEN, items: ['Account locked flag', 'High transaction count', 'Large transfer amounts'] },
  ];
  let cx = 0.6;
  cols.forEach(c => {
    addRoundRect(s, { x: cx, y: 1.6, w: 3.95, h: 3.3, fill: 'F8FAFC', line: { color: c.c, width: 2 }, shadow: true });
    addRoundRect(s, { x: cx + 1.37, y: 1.72, w: 1.2, h: 0.5, fill: c.c, shadow: false, radius: 0.25 });
    addText(s, c.t, { x: cx + 0.25, y: 1.76, w: 3.45, h: 0.45, size: 15, color: c.c, bold: true, align: 'center' });
    addBullet(s, c.items, { x: cx + 0.25, y: 2.5, w: 3.45, h: 2.2, size: 12.5, color: SLATE, spaceAfter: 9 });
    cx += 4.13;
  });

  addRoundRect(s, { x: 0.6, y: 5.15, w: 12.13, h: 1.75, fill: DARK, shadow: true });
  addText(s, 'Score → Action', { x: 0.95, y: 5.32, w: 11.5, h: 0.4, size: 15, color: CYAN, bold: true });
  addText(s, [
    { text: 'LOW  (<30)   →  MONITOR / ALLOW', options: { color: GREEN, bold: true } },
    { text: '   MEDIUM (30–59)  →  WARN', options: { color: AMBER, bold: true } },
    { text: '   HIGH (60–79)  →  WARN + PROTECT', options: { color: RED, bold: true } },
    { text: '   CRITICAL (≥80)  →  DISCONNECT + ALERT', options: { color: RED, bold: true } },
  ], { x: 0.95, y: 5.82, w: 11.5, h: 0.95, size: 13.5, color: LIGHT, align: 'center', lineSpacing: 1.4 });
}

// =========================================================
// SLIDE 6 — Demo Dashboard
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: DARK });
  addText(s, 'Demo Dashboard', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'Colorful security command center you can try right now', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: '94A3B8' });

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
    const x = 0.6 + col * 6.05;
    const y = dy + row * 1.78;
    addRoundRect(s, { x, y, w: 5.75, h: 1.6, fill: 'F8FAFC', line: { color: 'E2E8F0', width: 1 }, shadow: true });
    addRoundRect(s, { x: x + 0.2, y: y + 0.22, w: 0.42, h: 0.42, fill: i % 2 === 0 ? CYAN : AMBER, shadow: false, radius: 0.2 });
    addText(s, d.t, { x: x + 0.8, y: y + 0.16, w: 4.7, h: 0.4, size: 14, color: DARK, bold: true });
    addText(s, d.d, { x: x + 0.22, y: y + 0.68, w: 5.3, h: 0.85, size: 11.5, color: SLATE, lineSpacing: 1.1 });
  });

  addText(s, 'Open: http://localhost:8000/dashboard   ·   Backend: python -m backend.api.main', { x: 0.6, y: 6.95, w: 12, h: 0.35, size: 11, color: '64748B', align: 'center' });
}

// =========================================================
// SLIDE 7 — Android Architecture
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: RED });
  addText(s, 'Android Phase 2', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 34, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'Real-time call monitoring & auto-disconnect on-device', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'FECACA' });

  const arch = [
    { t: 'CallScreeningService', d: 'Listens for INCOMING_CALL → queries backend API → risk score → ALLOW / WARN / DISCONNECT.', c: CYAN },
    { t: 'InCallService (Foreground)', d: 'Live audio capture, real-time transcription, risk overlay, emergency buttons.', c: AMBER },
    { t: 'DisconnectCountdown', d: '5-second full-screen emergency UI → auto-disconnect → show 1930 helpline.', c: RED },
  ];
  let ax = 0.6;
  arch.forEach(a => {
    addRoundRect(s, { x: ax, y: 1.6, w: 3.95, h: 3.5, fill: 'F8FAFC', line: { color: a.c, width: 2 }, shadow: true });
    addRoundRect(s, { x: ax + 1.37, y: 1.72, w: 1.2, h: 0.5, fill: a.c, shadow: false, radius: 0.25 });
    addText(s, a.t, { x: ax + 0.25, y: 1.76, w: 3.45, h: 0.5, size: 14.5, color: a.c, bold: true, align: 'center' });
    addText(s, a.d, { x: ax + 0.22, y: 2.5, w: 3.5, h: 2.4, size: 12, color: SLATE, lineSpacing: 1.15 });
    ax += 4.13;
  });

  addText(s, [
    { text: 'Permissions: ', options: { bold: true, color: DARK } },
    { text: 'RECORD_AUDIO, READ_PHONE_STATE, FOREGROUND_SERVICE, INTERNET, DISCONNECT_PHONE_STATE', options: { color: SLATE } },
  ], { x: 0.6, y: 5.35, w: 12.1, h: 0.45, size: 12, color: SLATE });

  addRoundRect(s, { x: 0.6, y: 5.9, w: 12.13, h: 1.0, fill: DARK, shadow: false });
  addText(s, 'Fallback: AccessibilityService simulates END_CALL when system telephony permission is unavailable.', { x: 0.95, y: 6.05, w: 11.5, h: 0.7, size: 12.5, color: LIGHT, align: 'center', lineSpacing: 1.15 });
}

// =========================================================
// SLIDE 8 — Tech Stack & Roadmap
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: LIGHT });

  addRect(s, { x: 0, y: 0, w: 13.333, h: 1.15, fill: SLATE });
  addText(s, 'Tech Stack & Roadmap', { x: 0.6, y: 0.32, w: 12, h: 0.55, size: 32, color: LIGHT, bold: true, fontFace: THEME.headFontFace });
  addText(s, 'What we built and where we go next', { x: 0.6, y: 0.82, w: 12, h: 0.3, size: 14, color: 'CBD5E1' });

  // left: stack
  addRoundRect(s, { x: 0.6, y: 1.55, w: 5.9, h: 4.2, fill: 'F8FAFC', line: { color: 'E2E8F0', width: 1 }, shadow: true });
  addText(s, 'Tech Stack', { x: 0.95, y: 1.82, w: 5.2, h: 0.4, size: 17, color: DARK, bold: true });
  addBullet(s, [
    { text: 'FastAPI + Uvicorn (Python backend)', options: {} },
    { text: 'Gemini API (google-genai SDK)', options: {} },
    { text: 'Pydantic v2 (structured JSON output)', options: {} },
    { text: 'Kotlin / Android (CallScreeningService, InCallService)', options: {} },
    { text: 'HTML / CSS / JS (colorful dashboard)', options: {} },
    { text: 'python-dotenv, httpx, pytest', options: {} },
  ], { x: 0.95, y: 2.32, w: 5.25, h: 3.3, size: 13, color: SLATE, spaceAfter: 9 });

  // right: roadmap
  addRoundRect(s, { x: 6.8, y: 1.55, w: 5.93, h: 4.2, fill: DARK, shadow: true });
  addText(s, 'Roadmap', { x: 7.15, y: 1.82, w: 5.2, h: 0.4, size: 17, color: CYAN, bold: true });
  const road = [
    { t: 'Now', d: 'Demo backend + dashboard + Android docs', c: AMBER },
    { t: 'Next', d: 'Gemini live transcription + ONNX deepfake model', c: CYAN },
    { t: 'Later', d: 'Local encrypted storage + real 1930 integration', c: GREEN },
  ];
  let ry = 2.4;
  road.forEach(r => {
    addRoundRect(s, { x: 7.15, y: ry, w: 0.5, h: 0.5, fill: r.c, shadow: false, radius: 0.2 });
    addText(s, r.t, { x: 7.15, y: ry + 0.08, w: 0.5, h: 0.36, size: 12, color: LIGHT, bold: true, align: 'center' });
    addText(s, r.d, { x: 7.85, y: ry, w: 4.6, h: 0.6, size: 12, color: 'E2E8F0', lineSpacing: 1.1 });
    ry += 0.78;
  });

  addRoundRect(s, { x: 0.6, y: 6.0, w: 12.13, h: 0.95, fill: GREEN, shadow: false });
  addText(s, 'Hackathon-ready demo: run `python -m backend.api.main` and open `http://localhost:8000/dashboard`', { x: 0.95, y: 6.15, w: 11.5, h: 0.7, size: 13.5, color: LIGHT, align: 'center', lineSpacing: 1.2 });
}

// =========================================================
// SLIDE 9 — Thank You
// =========================================================
{
  const s = pres.addSlide();
  addRect(s, { x: 0, y: 0, w: 13.333, h: 7.5, fill: DARK });
  addRect(s, { x: 0, y: 0, w: 0.22, h: 7.5, fill: CYAN });

  addText(s, 'Thank You', { x: 0.9, y: 2.3, w: 11.5, h: 0.7, size: 48, color: LIGHT, bold: true, fontFace: THEME.headFontFace, align: 'center' });
  addText(s, 'SwaraGuard AI — Anti-Scam Call Protection', { x: 0.9, y: 3.15, w: 11.5, h: 0.45, size: 18, color: '94A3B8', align: 'center' });
  addText(s, 'Built for the Hackathon  ·  FastAPI · Gemini AI · Android', { x: 0.9, y: 3.7, w: 11.5, h: 0.4, size: 14, color: '64748B', align: 'center' });

  addText(s, 'Try it:  python -m backend.api.main  →  http://localhost:8000/dashboard', { x: 0.9, y: 4.7, w: 11.5, h: 0.45, size: 15, color: CYAN, bold: true, align: 'center' });
  addText(s, 'Questions?  SwaraGuard AI Team', { x: 0.9, y: 6.6, w: 11.5, h: 0.35, size: 11, color: '64748B', align: 'center' });
}

pres.writeFile({ fileName: 'SwaraGuard_Hackathon_Deck.pptx' }).then(() => {
  console.log('Deck written: SwaraGuard_Hackathon_Deck.pptx');
});
