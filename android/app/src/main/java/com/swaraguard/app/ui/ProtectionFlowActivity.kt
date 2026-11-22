package com.swaraguard.app.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.swaraguard.app.R
import com.swaraguard.app.databinding.ActivityProtectionFlowBinding
import com.swaraguard.app.model.ProtectionResponse
import com.swaraguard.app.model.RiskAnalysis
import com.swaraguard.app.network.ApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ProtectionFlowActivity : AppCompatActivity() {

    companion object {
        private const val REQUEST_CODE_PERMISSION_CALL = 200
        private val NEEDED_PERMISSIONS = arrayOf(
            Manifest.permission.CALL_PHONE
        )
    }

    private lateinit var binding: ActivityProtectionFlowBinding
    private val apiService = ApiClient.createService()
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var protectionResponse: ProtectionResponse? = null
    private var riskScore: Int = 0

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            initiateProtection()
        } else {
            Toast.makeText(this, "Call permission required for emergency dial", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityProtectionFlowBinding.inflate(layoutInflater)
        setContentView(binding.root)

        riskScore = intent.getIntExtra("risk_score", 0)

        setupUI()
    }

    private fun setupUI() {
        binding.apply {
            tvRiskScore.text = riskScore.toString()
            tvRiskLevel.text = if (riskScore >= 70) "HIGH RISK" else if (riskScore >= 40) "MEDIUM RISK" else "LOW RISK"

            btnCall1930.setOnClickListener { checkCallPermission() }
            btnFreezeAccount.setOnClickListener { initiateProtection() }
            btnOpenBankApps.setOnClickListener { openBankAppLinks() }
            btnSendSMS.setOnClickListener { sendFreezeSMS() }
            btnOpenDashboard.setOnClickListener { openDashboard() }
            btnBack.setOnClickListener { finish() }
            btnDone.setOnClickListener { finish() }
        }

        // Create simulated freeze
        createSimulatedFreeze()
    }

    private fun createSimulatedFreeze() {
        scope.launch {
            val result = createAccountFreeze()
            protectionResponse = result
            displayProtectionStatus(result)
        }
    }

    private suspend fun createAccountFreeze(): ProtectionResponse = withContext(Dispatchers.IO) {
        try {
            val response = apiService.simulateFreeze(
                com.swaraguard.app.network.FreezeRequest(
                    accountAlias = "Primary Account (XXXX1234)",
                    reason = if (riskScore >= 70) "High-risk scam call - potential OTP exposure" else "Suspicious call detected",
                    durationMinutes = 1440,
                    userId = "user_$(System.currentTimeMillis())"
                )
            ).execute()

            if (response.isSuccessful) {
                response.body() ?: ProtectionResponse()
            } else {
                ProtectionResponse()
            }
        } catch (e: Exception) {
            ProtectionResponse()
        }
    }

    private fun displayProtectionStatus(response: ProtectionResponse) {
        binding.apply {
            if (response.status == "SIMULATED_FREEZE_ACTIVE") {
                tvStatus.text = "Account Frozen (Simulated)"
                tvStatus.setCompoundDrawablesWithIntrinsicBounds(R.drawable.ic_baseline_check_circle_24dp, 0, 0, 0)
                tvStatus.setTextColor(ContextCompat.getColor(this@ProtectionFlowActivity, R.color.risk_low))

                tvFreezeExpiry.text = "Locked until: 24 hours"
                tvAccountAlias.text = response.accountAlias

                groupActions.visibility = android.view.View.VISIBLE
                groupDone.visibility = android.view.View.GONE
            } else {
                tvStatus.text = "Status: Ready"
                tvStatus.setCompoundDrawablesWithIntrinsicBounds(R.drawable.ic_baseline_error_24dp, 0, 0, 0)
                tvStatus.setTextColor(ContextCompat.getColor(this@ProtectionFlowActivity, R.color.risk_medium))
            }

            // Populate action buttons
            btnCall1930.text = "📞 Call 1930"
            btnOpenBankApps.text = "🏦 Open Bank App"
            btnSendSMS.text = "📱 Send Freeze SMS"
        }

        // Update progress
        binding.progressBar.progress = 100
    }

    private fun checkCallPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE)
            == PackageManager.PERMISSION_GRANTED) {
            placeEmergencyCall()
        } else {
            requestPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
        }
    }

    private fun placeEmergencyCall() {
        val intent = Intent(Intent.ACTION_CALL, Uri.parse("tel:1930"))
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CALL_PHONE)
            == PackageManager.PERMISSION_GRANTED) {
            startActivity(intent)
        }
    }

    private fun initiateProtection() {
        binding.progressBar.visibility = android.view.View.VISIBLE
        binding.tvProtectionStatus.text = "Initiating protection..."

        scope.launch {
            val result = createAccountFreeze()

            binding.apply {
                progressBar.visibility = android.view.View.GONE
                tvProtectionStatus.text = "Protection Active"
                tvProtectionStatus.setTextColor(ContextCompat.getColor(this@ProtectionFlowActivity, R.color.risk_high))
            }

            Toast.makeText(
                this@ProtectionFlowActivity,
                "Account simulation frozen for 24 hours\n\nNext steps:\n• Open your bank app\n• Change UPI PIN\n• Monitor transactions",
                Toast.LENGTH_LONG
            ).show()

            groupActions.visibility = android.view.View.VISIBLE
            groupDone.visibility = android.view.View.GONE
            protectionResponse = result
        }
    }

    private fun openBankAppLinks() {
        val bankApps = listOf(
            "hdfc://security/otp",
            "icici://freeze/transactions",
            "sbi://quickpay/block",
            "paytm://freeze"
        )

        // Find available bank app
        var launched = false
        for (url in bankApps) {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                startActivity(intent)
                launched = true
                break
            } catch (e: Exception) {
                // Bank app not installed, continue to next
            }
        }

        if (!launched) {
            // Fallback: show bank list
            showBankAppDialog()
        }
    }

    private fun showBankAppDialog() {
        val bankApps = arrayOf(
            "HDFC Bank",
            "ICICI Bank",
            "State Bank of India",
            "Axis Bank",
            "Kotak Bank"
        )

        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Open Bank App")
            .setItems(bankApps) { _, which ->
                when (which) {
                    0 -> openBankApp("hdfc://security/otp")
                    1 -> openBankApp("icici://freeze/transactions")
                    2 -> openBankApp("sbi://quickpay/block")
                    3 -> openBankApp("axis://security/verify")
                    4 -> openBankApp("kotak://lock/account")
                }
            }
            .show()
    }

    private fun openBankApp(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Bank app not available", Toast.LENGTH_SHORT).show()
        }
    }

    private fun sendFreezeSMS() {
        val smsContent = """
        SwaraGuard Alert: Scam call detected.
        Account XXXX1234 temporarily blocked.
        Call 1930 for assistance.
        """.trimIndent()

        val smsUri = Uri.parse("smsto:1930")
        val intent = Intent(Intent.ACTION_SENDTO, smsUri).apply {
            putExtra("sms_body", smsContent)
        }

        startActivity(intent)
    }

    private fun openDashboard() {
        val intent = Intent(this, DashboardActivity::class.java)
        startActivity(intent)
    }

    override fun onBackPressed() {
        // Show confirmation for exiting during high risk
        if (riskScore >= 70) {
            androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Exits During High Risk?")
                .setMessage("Are you sure you want to exit? The scam call is still detected as HIGH RISK.")
                .setPositiveButton("Yes, Exit") { _, _ -> super.onBackPressed() }
                .setNegativeButton("Cancel", null)
                .show()
        } else {
            super.onBackPressed()
        }
    }
}