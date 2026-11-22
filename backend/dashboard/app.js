let currentIsUnknownNumber = false;
let disconnectTimer = null;

async function updateDashboard() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();

        // Update Risk
        document.getElementById('riskValue').textContent = data.risk_score;
        document.getElementById('riskLevel').textContent = data.risk_level;
        document.getElementById('riskAction').textContent = getRiskAction(data.risk_level);

        // Update Account
        document.getElementById('accountBalance').textContent = `₹${data.account_balance}`;
        document.getElementById('accountStatus').textContent = data.account_status;
        document.getElementById('accountStatus').className = `status-badge status-${data.account_status.toLowerCase()}`;

        // Update Freeze Countdown
        const freezeCountdown = document.getElementById('freezeCountdown');
        const freezeTime = document.getElementById('freezeTime');
        const freezeMinutes = document.getElementById('freezeMinutes');

        if (data.active_lock && freezeMinutes) {
            freezeCountdown.style.display = 'block';
            freezeMinutes.textContent = 15;

            // Start or update countdown
            startFreezeCountdown(data.lock_expires_at);
        } else {
            freezeCountdown.style.display = 'none';
            if (disconnectTimer) {
                clearInterval(disconnectTimer);
                disconnectTimer = null;
            }
            document.getElementById('autoDisconnectBanner').style.display = 'none';
        }

        // Update Audit
        const auditList = document.getElementById('auditList');
        const auditRes = await fetch('/api/events');
        const auditData = await auditRes.json();

        if (auditData.events && auditData.events.length > 0) {
            auditList.innerHTML = auditData.events.slice(-10).reverse().map(e => `
                <div class="audit-item">
                    <span>[${e.timestamp.split('T')[1].split('.')[0]}]</span>
                    <strong>${e.event_type}</strong>: ${e.description}
                </div>
            `).join('');
        } else {
            auditList.innerHTML = '<p style="opacity: 0.7;">No events yet. Start analyzing audio to see events.</p>';
        }

        // Update Guardian Alert Status
        const guardianStatus = document.getElementById('guardianStatus');
        if (data.guardian_alerts > 0) {
            guardianStatus.innerHTML = '<span style="color: #ff6b6b;">⚠️ Guardian notification sent</span>';
            document.getElementById('guardianActions').style.display = 'block';
        } else {
            guardianStatus.innerHTML = '<span>✓ No alerts</span>';
            document.getElementById('guardianActions').style.display = 'none';
        }

    } catch (e) {
        console.error("Dashboard update failed", e);
    }
}

function getRiskAction(riskLevel) {
    switch (riskLevel) {
        case 'CRITICAL': return 'PROTECT_ACCOUNT';
        case 'HIGH': return 'WARN_USER';
        case 'MEDIUM': return 'WARN';
        default: return 'MONITOR';
    }
}

function startFreezeCountdown(lockExpiresAt) {
    const expires = new Date(lockExpiresAt);
    const now = new Date();

    const updateCountdown = () => {
        const remaining = Math.max(0, Math.floor((expires - new Date()) / 1000));
        if (remaining === 0) {
            clearInterval(disconnectTimer);
            document.getElementById('freezeCountdown').style.display = 'none';
            return;
        }
        document.getElementById('disconnectCount').textContent = Math.ceil(remaining / (1000 * 5));
    };

    updateCountdown();
    clearInterval(disconnectTimer);
    disconnectTimer = setInterval(updateCountdown, 5000);
}

async function runScenario(scenario) {
    const unknownToggle = document.getElementById('unknownToggle').checked;
    const isUnknownNumber = unknownToggle;

    try {
        // Show auto-disconnect banner for high-risk scenarios
        const isHighRisk = ['bank_scam', 'digital_arrest', 'telugu_scam', 'hinglish_scam'].includes(scenario);

        if (isHighRisk) {
            document.getElementById('autoDisconnectBanner').style.display = 'block';
            startDisconnectCountdown();
        } else {
            document.getElementById('autoDisconnectBanner').style.display = 'none';
            if (disconnectTimer) {
                clearInterval(disconnectTimer);
                disconnectTimer = null;
            }
        }

        // Make API call
        const res = await fetch(`/api/analyze-audio?demo=${scenario}&is_unknown_number=${isUnknownNumber}`);
        const data = await res.json();

        // Update risk display
        document.getElementById('riskValue').textContent = data.voice_risk_score;
        document.getElementById('riskLevel').textContent = data.risk_level;
        document.getElementById('riskAction').textContent = getRiskAction(data.risk_level);

        // Update verdict
        const verdictValue = document.getElementById('verdictValue');
        const suspiciousIndicators = document.getElementById('suspiciousIndicators');
        const userAdvice = document.getElementById('userAdvice');

        if (data.voice_risk_score >= 80) {
            verdictValue.textContent = 'HIGH RISK SCAM';
            verdictValue.style.background = 'linear-gradient(135deg, #ff6b6b, #ee5a5a)';
            verdictValue.style.color = 'white';
            suspiciousIndicators.style.display = 'flex';
            userAdvice.innerHTML = '<p><strong>Action Required:</strong> DO NOT SHARE any information. Disconnection will begin in 5 seconds.</p>';
        } else if (data.voice_risk_score >= 60) {
            verdictValue.textContent = 'SUSPICIOUS';
            verdictValue.style.background = 'rgba(255, 107, 107, 0.2)';
            verdictValue.style.color = '#ff6b6b';
            suspiciousIndicators.style.display = 'flex';
            userAdvice.innerHTML = '<p><strong>Warning:</strong> Be cautious. Verify identity before sharing any details.</p>';
        } else {
            verdictValue.textContent = 'SAFE';
            verdictValue.style.background = 'rgba(78, 205, 196, 0.2)';
            verdictValue.style.color = '#4ecdc4';
            suspiciousIndicators.style.display = 'none';
            userAdvice.innerHTML = '<p style="opacity: 0.8;">Continue normal conversation...</p>';
        }

        updateDashboard();

    } catch (e) {
        console.error("Analysis failed", e);
    }
}

function startDisconnectCountdown() {
    let count = 5;
    const countEl = document.getElementById('disconnectCount');

    const interval = setInterval(() => {
        count--;
        countEl.textContent = count;

        if (count <= 0) {
            clearInterval(interval);
            // Simulate disconnection banner
            countEl.textContent = '0';
        }
    }, 1000);
}

document.getElementById('btnReset').addEventListener('click', async () => {
    await fetch('/api/reset', { method: 'POST' });
    updateDashboard();
});

document.getElementById('btnFreeze').addEventListener('click', async () => {
    const res = await fetch('/api/freeze-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Manual demo freeze' })
    });
    updateDashboard();
});

document.getElementById('btnGuardianAlert').addEventListener('click', async () => {
    const data = await fetch('/api/dashboard').then(r => r.json());
    await fetch('/api/guardian-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            risk_level: data.risk_level,
            risk_score: data.risk_score,
            reasons: 'High risk detected in voice analysis'
        })
    });
    updateDashboard();
});

document.getElementById('btnCall1930').addEventListener('click', () => {
    // Show confirmation for demo
    alert('Calling 1930...\n\nThis is the Indian Cyber Crime Helpline.\nIn a real scenario, this would initiate a phone call to report the scam.');
});

// Unknown number toggle listener
document.getElementById('unknownToggle').addEventListener('change', function() {
    currentIsUnknownNumber = this.checked;
    // Visual feedback
    const badge = document.querySelector('.demo-badge');
    if (this.checked) {
        badge.textContent = 'UNKNOWN NUMBER';
        badge.style.background = 'linear-gradient(135deg, #ff6b6b, #ee5a5a)';
    } else {
        badge.textContent = 'DEMO MODE';
        badge.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
    }
});

setInterval(updateDashboard, 5000);
updateDashboard();