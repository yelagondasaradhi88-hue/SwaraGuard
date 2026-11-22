"""
Fraud Call Shield - Interactive Hackathon Streamlit Demo UI.
Simulates customer phone events, bank security gating, and guardian escalation.
Designed with high contrast, large typography, and zero-confusion controls.
"""

import os
import time
from datetime import datetime, timezone
import requests
import streamlit as st

# Configure Page
st.set_page_config(
    page_title="Fraud Call Shield | AI Defense Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished presentation readability
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #dee2e6;
        margin-bottom: 12px;
    }
    .badge-active {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-frozen {
        background-color: #dc3545;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    .warn-box {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 12px;
        margin-bottom: 16px;
        border-radius: 4px;
        font-size: 1.05rem;
    }
    .freeze-box {
        background-color: #f8d7da;
        border-left: 6px solid #dc3545;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 4px;
        font-size: 1.15rem;
        font-weight: 600;
        color: #721c24;
    }
    .guardian-card {
        background-color: #e8f4fd;
        border-left: 6px solid #007bff;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def check_api_health():
    try:
        r = requests.get(f"{API_BASE_URL}/account", timeout=1.5)
        return r.status_code == 200, r.json() if r.status_code == 200 else {}
    except Exception:
        return False, {}


def send_event(event_type: str, details: dict = None):
    try:
        r = requests.post(
            f"{API_BASE_URL}/device-event",
            json={"event_type": event_type, "details": details or {}},
            timeout=3.0
        )
        return r.json()
    except Exception as e:
        st.error(f"Failed to communicate with API: {e}")
        return None


def fetch_events_and_audit():
    try:
        r = requests.get(f"{API_BASE_URL}/events", timeout=2.0)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


# ---------------- SIDEBAR CONTROLS ----------------
api_online, account_info = check_api_health()

with st.sidebar:
    st.title("🛡️ Fraud Call Shield")
    st.caption("AI Telemetry & Pre-Transfer Payment Freeze")

    if api_online:
        st.success(f"🟢 Mock Bank API: Connected (`{API_BASE_URL}`)")
    else:
        st.error(f"🔴 API Offline. Run:\n`uvicorn api.main:app --reload`")

    st.divider()

    if st.button("🔄 Reset Demo State", use_container_width=True, type="secondary"):
        try:
            requests.post(f"{API_BASE_URL}/reset", timeout=2.0)
            st.toast("State successfully reset!", icon="✅")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Reset failed: {e}")

    st.subheader("📋 Session Audit Trail")
    events_payload = fetch_events_and_audit()
    audit_logs = events_payload.get("audit_log", [])

    if audit_logs:
        for log in audit_logs[:12]:
            ts_short = log["timestamp"][11:19]
            with st.expander(f"⏱️ {ts_short} | {log['action']}"):
                st.json(log["details"])
    else:
        st.info("No audit entries logged yet.")


# ---------------- MAIN APP TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "📱 Tab 1: Customer Phone Simulator",
    "🏦 Tab 2: Mock Bank App",
    "👨‍👩‍👦 Tab 3: Family Guardian"
])

current_eval = events_payload.get("current_evaluation", {})
current_score = current_eval.get("score", account_info.get("current_score", 0))
current_tier = current_eval.get("tier", account_info.get("tier", "NORMAL"))
is_frozen = account_info.get("status") == "FROZEN"

# ==============================================================================
# TAB 1: CUSTOMER PHONE SIMULATOR
# ==============================================================================
with tab1:
    st.subheader("📱 On-Device Risk Telemetry Simulator")
    st.write(
        "Simulates raw phone signals without storing or recording audio. "
        "Watches the chain of risky actions leading up to unauthorized fund transfers."
    )

    # Risk Meter & Status Top Banner
    col_score, col_tier, col_status, col_latency = st.columns(4)
    with col_score:
        st.metric("Risk Score", f"{current_score} / 100")
    with col_tier:
        tier_emojis = {"NORMAL": "🟢 NORMAL", "WARN": "🟡 WARN", "SOFT_PROTECT": "🟠 SOFT PROTECT", "FREEZE": "🔴 FREEZE"}
        st.metric("Threat Tier", tier_emojis.get(current_tier, current_tier))
    with col_status:
        st.metric("Bank Status", "FROZEN 🔒" if is_frozen else "ACTIVE 🔓")
    with col_latency:
        st.metric("Engine Latency", f"{events_payload.get('last_decision_ms', 0):.2f} ms")

    # Progress bar with color
    st.progress(current_score / 100.0)

    # Dynamic Alert Banners
    if is_frozen or current_tier == "FREEZE":
        st.markdown(
            """
            <div class="freeze-box">
                🚨 OUTGOING PAYMENTS FROZEN FOR 30 MINUTES!<br>
                <span style="font-size: 0.95rem; font-weight: normal;">
                Critical multi-step scam chain detected. Incoming credits are still permitted, but all outbound
                transfers are halted until identity verification. Family Guardian notified.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif current_tier == "WARN":
        st.markdown(
            """
            <div class="warn-box">
                ⚠️ <b>Security Alert:</b> Banks and government officials NEVER ask you to install apps
                like AnyDesk, grant accessibility permissions, or share your screen.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif current_tier == "SOFT_PROTECT":
        st.info("🛡️ **SOFT PROTECT:** Elevated risk pattern detected. Outgoing payments require step-up security verification.")

    st.markdown("### ⚡ Interactive Telemetry Triggers")

    url_input = st.text_input("Simulated URL for Link Opened:", value="https://sbi-kyc-update.xyz/verify-account.apk")

    # Action Buttons Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📞 1. Unknown Call Active", use_container_width=True):
            res = send_event("unknown_call_active", {"caller": "+91-99887-11223"})
            st.toast("Triggered: Unknown Call (+25 pts)", icon="📞")
            time.sleep(0.3)
            st.rerun()

        if st.button("🔗 2. Open Phishing Link", use_container_width=True):
            res = send_event("link_opened", {"url": url_input})
            st.toast("Triggered: Link Opened (+15 pts + phishing detection)", icon="🔗")
            time.sleep(0.3)
            st.rerun()

    with c2:
        if st.button("📦 3. Sideload APK", use_container_width=True):
            res = send_event("apk_sideloaded", {"package": "com.quick.kyc.update"})
            st.toast("Triggered: APK Sideloaded (+30 pts)", icon="📦")
            time.sleep(0.3)
            st.rerun()

        if st.button("🖥️ 4. Open AnyDesk", use_container_width=True):
            res = send_event("remote_access_app_installed_or_opened", {"app_name": "AnyDesk"})
            st.toast("Triggered: Remote Access App (+35 pts)", icon="🖥️")
            time.sleep(0.3)
            st.rerun()

    with c3:
        if st.button("🛡️ 5. Grant Accessibility", use_container_width=True):
            res = send_event("accessibility_or_device_admin_permission_granted", {"permission": "AccessibilityService"})
            st.toast("Triggered: Accessibility Granted (+30 pts)", icon="🛡️")
            time.sleep(0.3)
            st.rerun()

        if st.button("📱 6. Start Screen Share", use_container_width=True):
            res = send_event("screen_sharing_started", {"client": "MediaProjection"})
            st.toast("Triggered: Screen Sharing Started (+25 pts)", icon="📱")
            time.sleep(0.3)
            st.rerun()

    with c4:
        if st.button("🔑 7. Receive OTP", use_container_width=True):
            res = send_event("otp_received_during_risky_session", {"sender": "VK-HDFCBK"})
            st.toast("Triggered: OTP Captured (+20 pts)", icon="🔑")
            time.sleep(0.3)
            st.rerun()

        if st.button("🏦 8. Open Bank App", use_container_width=True):
            res = send_event("bank_app_opened_after_risky_events", {"app": "YourBankMobile"})
            st.toast("Triggered: Bank App Opened (+10 pts)", icon="🏦")
            time.sleep(0.3)
            st.rerun()

    st.markdown("---")
    # Automated Multi-Step Scenario Player
    st.markdown("### 🎬 Automated Attack Chain Demonstration")
    st.write("Fires the complete scam sequence step-by-step with live progression and demonstrates automatic freeze **before** money moves.")

    if st.button("▶️ Play Full Scam Scenario (Live Timeline)", type="primary", use_container_width=True):
        scenario_steps = [
            ("unknown_call_active", {"caller": "+91-99887-11223"}, "📞 Unknown caller initiates call"),
            ("link_opened", {"url": "https://sbi-kyc-update.xyz/verify-account.apk"}, "🔗 User clicks SMS phishing link"),
            ("apk_sideloaded", {"package": "com.quick.kyc.update"}, "📦 Untrusted APK sideloaded from browser"),
            ("remote_access_app_installed_or_opened", {"app_name": "AnyDesk"}, "🖥️ AnyDesk remote viewer launched"),
            ("accessibility_or_device_admin_permission_granted", {"service": "AccessibilityService"}, "🛡️ Victim duped into granting Accessibility"),
            ("screen_sharing_started", {"display": "VirtualDisplay"}, "📱 Real-time screen sharing begins"),
            ("otp_received_during_risky_session", {"sender": "VK-BANK"}, "🔑 Transaction OTP arrives on screen"),
            ("bank_app_opened_after_risky_events", {"app": "YourBankMobile"}, "🏦 Bank app launched by victim under guidance")
        ]

        progress_container = st.empty()
        timeline_box = st.empty()
        accumulated_text = []

        for idx, (ev_name, ev_meta, desc) in enumerate(scenario_steps, 1):
            r = send_event(ev_name, ev_meta)
            score_now = r.get("score", 0) if r else 0
            tier_now = r.get("tier", "NORMAL") if r else "NORMAL"
            accumulated_text.append(f"**Step {idx}/8:** {desc} -> Score: **{score_now}** ({tier_now})")
            timeline_box.markdown("\n\n".join(accumulated_text))
            progress_container.progress(idx / len(scenario_steps))
            time.sleep(1.0)

        st.success("✅ Attack sequence completed. The account is now proactively FROZEN before money can be transferred!")
        time.sleep(1.0)
        st.rerun()

    # Event timeline list
    st.markdown("### ⏱️ Active 15-Minute Window Telemetry")
    window_events = events_payload.get("sliding_window_events", [])
    if window_events:
        for ev in reversed(window_events):
            t_str = ev.get("timestamp", "")[11:19]
            st.markdown(f"- `[{t_str}]` **{ev.get('event_type')}** — Details: `{ev.get('details')}`")
    else:
        st.write("No active events in sliding window.")


# ==============================================================================
# TAB 2: MOCK BANK APP
# ==============================================================================
with tab2:
    st.subheader("🏦 Mock NetBanking Portal")

    # Account Snapshot Card
    bal = account_info.get("balance", 50000.0)
    acc_no = account_info.get("account_no", "XXXX1234")
    user_name = account_info.get("name", "Demo User")
    status_str = account_info.get("status", "ACTIVE")
    frozen_until = account_info.get("frozen_until")

    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">{user_name}</h3>
                <span style="color: #6c757d;">Account: <b>{acc_no}</b> | Protected Profile: <b>Enabled</b></span>
            </div>
            <div>
                <span class="{'badge-frozen' if status_str == 'FROZEN' else 'badge-active'}">{status_str}</span>
            </div>
        </div>
        <hr style="margin: 12px 0;">
        <h1 style="margin: 0; color: #1e3d59;">₹{bal:,.2f}</h1>
        <small style="color: #6c757d;">Available Balance (INR)</small>
        {f'<div style="margin-top: 8px; color: #dc3545; font-weight: bold;">🔒 Auto-Unfreeze scheduled at: {frozen_until[11:19]} UTC</div>' if frozen_until else ''}
    </div>
    """, unsafe_allow_html=True)

    # Fund Transfer Section
    st.markdown("### 💸 Send Money")

    if status_str == "FROZEN":
        st.error("⛔ **OUTGOING TRANSFERS PAUSED FOR YOUR SAFETY.** Your bank will call you to verify your identity.")

    with st.form("transfer_form"):
        col_payee, col_amt = st.columns(2)
        with col_payee:
            target_payee = st.text_input("Payee Account / VPA", value="SCAMMER-9999", help="Known payees: RENT-0001, GROCER-0002")
        with col_amt:
            transfer_amount = st.number_input("Amount (₹)", min_value=100.0, max_value=50000.0, value=40000.0, step=1000.0)

        transfer_submitted = st.form_submit_button("Initiate Transfer", use_container_width=True, type="primary")

    if transfer_submitted:
        with st.spinner("Evaluating risk and executing bank controls..."):
            try:
                tx_res = requests.post(
                    f"{API_BASE_URL}/transfer",
                    json={"to_account": target_payee, "amount": transfer_amount},
                    timeout=3.0
                ).json()

                decision = tx_res.get("decision")
                st.session_state["last_tx_response"] = tx_res

                if decision == "ALLOW":
                    st.success(f"✅ {tx_res.get('message')}")
                    st.caption(f"Latency: {tx_res.get('processing_ms')} ms | Risk Score: {tx_res.get('score')}")
                    time.sleep(1.0)
                    st.rerun()
                elif decision == "STEP_UP":
                    st.warning(f"🛡️ {tx_res.get('message')}")
                    st.session_state["step_up_question"] = tx_res.get("security_question")
                elif decision == "HOLD":
                    st.error(f"🛑 {tx_res.get('message')}")
                    if tx_res.get("reasons"):
                        st.markdown("**Reasons:**")
                        for r in tx_res.get("reasons"):
                            st.write(f"- {r}")
                    time.sleep(1.0)
                    st.rerun()
            except Exception as e:
                st.error(f"Transfer error: {e}")

    # Handle Step-Up Verification Form if pending
    if st.session_state.get("step_up_question"):
        st.markdown("#### 🔐 Step-Up Identity Verification")
        st.write(f"**Security Question:** {st.session_state.get('step_up_question')}")
        step_up_ans = st.text_input("Your Security Answer (Hint: Sharma):", key="step_up_input")
        if st.button("Submit Step-Up Verification"):
            try:
                verify_res = requests.post(
                    f"{API_BASE_URL}/verify-transfer",
                    json={"answer": step_up_ans},
                    timeout=2.0
                )
                if verify_res.status_code == 200:
                    st.success("✅ Verification successful! Transfer completed.")
                    st.session_state.pop("step_up_question", None)
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error("❌ Incorrect answer. Transfer held.")
            except Exception as e:
                st.error(f"Verification call failed: {e}")

    st.markdown("---")
    # Bank Callback Simulation Card
    st.markdown("### 📞 Simulated Bank Identity Verification Callback")
    st.caption("When an account is frozen, the fraud desk calls the customer to confirm legitimacy and unfreeze the account.")

    try:
        cb_info = requests.get(f"{API_BASE_URL}/bank-callback", timeout=2.0).json()
    except Exception:
        cb_info = {}

    with st.expander("🎙️ Click to Open Simulated Bank Call Screen", expanded=(status_str == "FROZEN")):
        st.markdown(f"**Caller:** ☎️ `{cb_info.get('caller_id', 'YourBank Fraud Safety Desk')}`")
        st.markdown(f"""
        > *"{cb_info.get('script', '')}"*
        """)

        st.markdown("**Identity Challenge Questions:**")
        q1_input = st.text_input("1. What is your mother's maiden name? (Hint: Sharma)", value="Sharma")
        q2_input = st.text_input("2. What city was your first job in? (Hint: Pune)", value="Pune")

        if st.button("Submit Verified Answers & Unfreeze Account", type="primary"):
            try:
                unfreeze_res = requests.post(
                    f"{API_BASE_URL}/verify-and-unfreeze",
                    json={"q1_answer": q1_input, "q2_answer": q2_input},
                    timeout=2.0
                )
                if unfreeze_res.status_code == 200:
                    st.success("🎉 Identity Confirmed! Account restored to ACTIVE status.")
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error("❌ Answers did not match customer profile. Account remains FROZEN.")
            except Exception as e:
                st.error(f"Failed to submit answers: {e}")


# ==============================================================================
# TAB 3: FAMILY GUARDIAN
# ==============================================================================
with tab3:
    st.subheader("👨‍👩‍👦 Family Guardian Oversight Portal")
    guardian_data = account_info.get("guardian", {"name": "Family Guardian", "phone": "+91-98765-00000"})
    st.write(
        f"Protected User: **{account_info.get('name', 'Demo User')}** | "
        f"Designated Guardian: **{guardian_data.get('name')}** ({guardian_data.get('phone')})"
    )

    guardian_alerts = events_payload.get("guardian_notifications", [])

    if guardian_alerts:
        st.markdown("### 🚨 High-Priority Guardian Alerts")
        for alert in guardian_alerts:
            st.markdown(f"""
            <div class="guardian-card">
                <b>🚨 Time:</b> {alert.get('timestamp', '')[11:19]} UTC<br>
                <b>Notification:</b> Account transfers held due to suspicious scam chain.<br>
                <b>Risk Signals Detected:</b>
                <ul>
                    {''.join(f'<li>{r}</li>' for r in alert.get('reasons', []))}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Guardian Override Actions:")
        col_appr, col_deny = st.columns(2)
        with col_appr:
            if st.button("✅ I Am With User & Approve Release", use_container_width=True, type="primary"):
                try:
                    res = requests.post(f"{API_BASE_URL}/guardian-decision", json={"approve": True}, timeout=2.0)
                    if res.status_code == 200:
                        st.success("Hold released! Account restored to ACTIVE.")
                        time.sleep(1.0)
                        st.rerun()
                except Exception as e:
                    st.error(f"Action failed: {e}")

        with col_deny:
            if st.button("🛑 Suspected Fraud: Keep Frozen", use_container_width=True):
                try:
                    res = requests.post(f"{API_BASE_URL}/guardian-decision", json={"approve": False}, timeout=2.0)
                    if res.status_code == 200:
                        st.warning("Protective hold confirmed and maintained.")
                        time.sleep(1.0)
                        st.rerun()
                except Exception as e:
                    st.error(f"Action failed: {e}")
    else:
        st.info("No safety alerts dispatched to Family Guardian at this time.")
