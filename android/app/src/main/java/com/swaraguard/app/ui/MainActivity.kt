package com.swaraguard.app.ui

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.swaraguard.app.R
import com.swaraguard.app.databinding.ActivityMainBinding
import com.swaraguard.app.model.RiskAnalysis
import com.swaraguard.app.service.CallAnalysisService

class MainActivity : AppCompatActivity() {

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 100
        private val REQUIRED_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.FOREGROUND_SERVICE,
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.POST_NOTIFICATIONS
            )
        } else {
            arrayOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.FOREGROUND_SERVICE,
                Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_CALL_LOG
            )
        }
    }

    private lateinit var binding: ActivityMainBinding
    private var analysisService: CallAnalysisService? = null

    // Start a call recording/analysis
    private val startCallAnalysis = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        // Handle result
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setupWindowInsets()
        setupAudioManager()

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupPermissions()
        setupUI()
    }

    private fun setupWindowInsets() {
        // Handle system insets
        WindowCompat.setDecorFitsSystemWindows(window, false)
    }

    private fun setupAudioManager() {
        val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
        audioManager.requestAudioFocus(null, AudioManager.STREAM_VOICE_CALL, AudioManager.AUDIOFOCUS_GAIN)
    }

    private fun setupPermissions() {
        if (!hasAllPermissions()) {
            requestPermissions()
        } else {
            setupPermissionRationale()
        }
    }

    private fun hasAllPermissions(): Boolean {
        return REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
    }

    private fun setupPermissionRationale() {
        val prefs = getSharedPreferences("swaraguard_prefs", Context.MODE_PRIVATE)
        val shownRationale = prefs.getBoolean("permissions_rationale_shown", false)

        if (!shownRationale) {
            showPermissionRationaleDialog()
            prefs.edit().putBoolean("permissions_rationale_shown", true).apply()
        }
    }

    private fun showPermissionRationaleDialog() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Permissions Required")
            .setMessage("""
                SwaraGuard needs these permissions to:

                • Record call audio from speakerphone
                • Monitor outgoing transactions
                • End scam calls automatically
                • Show notifications for high-risk calls

                You can manage these in Settings > Apps > SwaraGuard > Permissions.
            """.trimIndent())
            .setPositiveButton("Grant Permissions") { _, _ ->
                requestPermissions()
            }
            .setNegativeButton("Exit App") { _, _ ->
                finish()
            }
            .show()
    }

    private fun setupUI() {
        binding.apply {
            tvAppName.text = "SwaraGuard"
            tvDescription.text = "AI-powered scam call protection"

            btnStartAnalysis.setOnClickListener {
                if (hasAllPermissions()) {
                    startCallAnalysisIntent()
                } else {
                    requestPermissions()
                }
            }

            btnDemoMode.setOnClickListener {
                startActivity(Intent(this@MainActivity, DemoModeActivity::class.java))
            }

            btnSettings.setOnClickListener {
                showSettingsDialog()
            }
        }

        // Setup risk indicators
        setupRiskIndicators()
    }

    private fun startCallAnalysisIntent() {
        // Start the call analysis service
        val intent = Intent(this, CallAnalysisService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }

        Toast.makeText(this, "Listening for scam patterns...", Toast.LENGTH_SHORT).show()
    }

    private fun setupRiskIndicators() {
        binding.layoutRiskIndicator.apply {
            setRiskLevel(0)
        }
    }

    private fun showSettingsDialog() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("SwaraGuard Settings")
            .setItems(arrayOf("Permission Settings", "Demo Mode", "Call Logs", "About")) { _, which ->
                when (which) {
                    0 -> openAppSettings()
                    1 -> startActivity(Intent(this@MainActivity, DemoModeActivity::class.java))
                    2 -> Toast.makeText(this@MainActivity, "Call logs view coming soon", Toast.LENGTH_SHORT).show()
                    3 -> showAboutDialog()
                }
            }
            .show()
    }

    private fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.data = android.net.Uri.fromParts("package", packageName, null)
        startActivity(intent)
    }

    private fun showAboutDialog() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("About SwaraGuard")
            .setMessage("""
                SwaraGuard v1.0

                AI-powered scam call detection for Indian phone users.

                Features:
                • Real-time deepfake voice detection
                • Scam pattern recognition (Hindi, Telugu, English)
                • Automatic call termination on high-risk
                • Simulated bank freeze protection

                Track: AI & Generative AI
            """.trimIndent())
            .setPositiveButton("OK", null)
            .show()
    }

    private fun requestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ActivityCompat.requestPermissions(
                this,
                REQUIRED_PERMISSIONS,
                REQUEST_CODE_PERMISSIONS
            )
        } else {
            ActivityCompat.requestPermissions(
                this,
                REQUIRED_PERMISSIONS,
                REQUEST_CODE_PERMISSIONS
            )
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                Toast.makeText(this, "All permissions granted", Toast.LENGTH_SHORT).show()
            } else {
                if (shouldShowRequestPermissionRationale(Manifest.permission.RECORD_AUDIO)) {
                    showPermissionRationaleDialog()
                } else {
                    Toast.makeText(this, "Some permissions denied. App may not work correctly.", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        analysisService = null
    }
}