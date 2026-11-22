package com.swaraguard.app.ui

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.os.Bundle
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.swaraguard.app.R
import com.swaraguard.app.databinding.ActivityDemoModeBinding
import com.swaraguard.app.model.RiskAnalysis
import com.swaraguard.app.network.ApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

class DemoModeActivity : AppCompatActivity() {

    companion object {
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
    }

    private lateinit var binding: ActivityDemoModeBinding
    private val apiService = ApiClient.createService()
    private val scope = CoroutineScope(Dispatchers.Main + Job())
    private var mediaPlayer: MediaPlayer? = null

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            openSampleAudio()
        } else {
            Toast.makeText(this, "Storage permission required for demo mode", Toast.LENGTH_SHORT).show()
            finish()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityDemoModeBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
    }

    private fun setupUI() {
        binding.apply {
            tvTitle.text = "Demo Mode"
            tvDescription.text = "Analyze a pre-recorded scam call recording"

            btnSelectSample.setOnClickListener {
                checkStoragePermission()
            }

            btnBack.setOnClickListener {
                finish()
            }
        }

        // Try to load sample audio from assets
        loadSampleAudio()
    }

    private fun checkStoragePermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
            == PackageManager.PERMISSION_GRANTED) {
            openSampleAudio()
        } else {
            requestPermissionLauncher.launch(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
    }

    private fun loadSampleAudio() {
        // Copy sample audio from assets to cache directory
        try {
            val sampleFile = File(cacheDir, "sample_scam_call.m4a")
            if (!sampleFile.exists()) {
                assets.open("sample_scam_call.m4a").use { input ->
                    sampleFile.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }
            }
            binding.btnSelectSample.isEnabled = sampleFile.exists()
            binding.btnSelectSample.text = if (sampleFile.exists()) "Play & Analyze Sample" else "Loading Sample..."
        } catch (e: Exception) {
            binding.btnSelectSample.isEnabled = false
            binding.btnSelectSample.text = "Sample not available"
        }
    }

    private fun openSampleAudio() {
        try {
            val sampleFile = File(cacheDir, "sample_scam_call.m4a")
            if (sampleFile.exists()) {
                playAndAnalyze(sampleFile)
            } else {
                Toast.makeText(this, "Sample file not found", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun playAndAnalyze(file: File) {
        try {
            mediaPlayer = MediaPlayer.create(this, android.net.Uri.fromFile(file))
            mediaPlayer?.isLooping = true
            mediaPlayer?.setOnPreparedListener {
                btnPlayPause()
                it.start()
                analyzeDemoAudio(file)
            }
            mediaPlayer?.setOnErrorListener { _, _, _ ->
                Toast.makeText(this, "Error playing audio", Toast.LENGTH_SHORT).show()
                false
            }
            mediaPlayer?.prepareAsync()
        } catch (e: Exception) {
            Toast.makeText(this, "Could not play audio: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun analyzeDemoAudio(file: File) {
        binding.progressBar.visibility = android.view.View.VISIBLE
        binding.tvAnalysisStatus.text = "Analyzing..."

        scope.launch {
            val result = analyzeAudioFile(file)
            displayResult(result)
        }
    }

    private suspend fun analyzeAudioFile(file: File): RiskAnalysis = withContext(Dispatchers.IO) {
        try {
            val requestBody = file.asRequestBody("audio/mp4".toMediaTypeOrNull())
            val multipart = MultipartBody.Part.createFormData("file", file.name, requestBody)

            val response = apiService.analyzeAudio(multipart).execute()
            if (response.isSuccessful) {
                response.body() ?: RiskAnalysis()
            } else {
                RiskAnalysis()
            }
        } catch (e: Exception) {
            RiskAnalysis()
        }
    }

    private fun displayResult(analysis: RiskAnalysis) {
        binding.progressBar.visibility = android.view.View.GONE

        binding.apply {
            tvAnalysisStatus.text = when (analysis.verdict) {
                "HIGH_RISK_SCAM" -> "🚨 HIGH RISK SCAM DETECTED"
                "SUSPICIOUS" -> "⚠️ Suspicious Activity Detected"
                else -> "✓ Call appears safe"
            }

            tvTranscript.text = analysis.transcript.ifEmpty { "No transcript available" }
            tvRiskScore.text = "${analysis.riskScore}/100"
            tvVerdict.text = analysis.verdict

            // Show detected tactics
            val tacticsText = if (analysis.scamTactics.isNotEmpty() && analysis.scamTactics[0] != "None") {
                analysis.scamTactics.joinToString("\n")
            } else {
                "None detected"
            }
            tvScamTactics.text = tacticsText

            // Update risk indicator
            binding.riskIndicator.setRiskLevel(analysis.riskScore)

            // Show appropriate advice
            if (analysis.riskLevel == RiskAnalysis.RiskLevel.HIGH) {
                showWarningDialog(analysis)
            }

            binding.tvAnalysisStatus.visibility = android.view.View.GONE
            binding.groupResult.visibility = android.view.View.VISIBLE
        }

        Toast.makeText(this, "Analysis complete: ${analysis.verdict}", Toast.LENGTH_LONG).show()
    }

    private fun showWarningDialog(analysis: RiskAnalysis) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("HIGH RISK DETECTED")
            .setMessage("""
                This appears to be a scam call!

                Risk Score: ${analysis.riskScore}
                Tactics: ${analysis.scamTactics.joinToString(", ")}

                Recommended actions:
                1. End the call immediately
                2. Do not share any personal information
                3. Activate scam protection flow
            """.trimIndent())
            .setPositiveButton("Activate Protection") { _, _ ->
                // Navigate to protection flow
                val intent = Intent(this, ProtectionFlowActivity::class.java)
                intent.putExtra("risk_score", analysis.riskScore)
                intent.putExtra("verdict", analysis.verdict)
                intent.putExtra("transcript", analysis.transcript)
                startActivity(intent)
            }
            .setNegativeButton("End Call", null)
            .show()
    }

    private fun btnPlayPause() {
        mediaPlayer?.setOnCompletionListener {
            binding.btnPlayPause.text = "Stop"
        }
    }

    override fun onBackPressed() {
        mediaPlayer?.release()
        super.onBackPressed()
    }

    override fun onDestroy() {
        super.onDestroy()
        mediaPlayer?.release()
        mediaPlayer = null
    }
}