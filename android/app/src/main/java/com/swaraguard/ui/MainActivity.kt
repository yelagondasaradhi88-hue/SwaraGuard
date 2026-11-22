package com.swaraguard.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private val REQUEST_CODE_PERMISSIONS = 100
    private val REQUIRED_PERMISSIONS = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.FOREGROUND_SERVICE,
        Manifest.permission.READ_PHONE_STATE,
        Manifest.permission.POST_NOTIFICATIONS
    )

    private lateinit var findViewById: (Int) -> Int
    private lateinit var tvRiskLevel: TextView
    private lateinit var tvRiskScore: TextView
    private lateinit var tvTranscript: TextView
    private lateinit var btnStart: Button
    private lateinit var btnDemo: Button

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startService(Intent(this, AudioMonitoringService::class.java))
        } else {
            Toast.makeText(this, "Permissions required", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<Int>(R.id.tvRiskLevel).also { tvRiskLevel ->
            tvRiskLevel = tvRiskLevel
        }
        findViewById<Int>(R.id.tvRiskScore).also { tvRiskScore ->
            tvRiskScore = tvRiskScore
        }
        findViewById<Int>(R.id.tvTranscript).also { tvTranscript ->
            tvTranscript = tvTranscript
        }
        findViewById<Int>(R.id.btnStart).also { btnStart ->
            btnStart.setOnClickListener {
                if (hasPermissions()) {
                    startService(Intent(this, AudioMonitoringService::class.java))
                    Toast.makeText(this, "Monitoring active", Toast.LENGTH_SHORT).show()
                } else {
                    requestPermissions()
                }
            }
        }
        findViewById<Int>(R.id.btnDemo).also { btnDemo ->
            btnDemo.setOnClickListener {
                startActivity(Intent(this, DemoActivity::class.java))
            }
        }

        setupUI()
    }

    private fun setupUI() {
        findViewById<Int>(R.id.tvRiskLevel).text = "Risk Level: LOW"
        findViewById<Int>(R.id.tvRiskScore).text = "Score: 0%"
        findViewById<Int>(R.id.tvTranscript).text = "No analysis"
        findViewById<Int>(R.id.btnStart).text = "Start Monitoring"
        findViewById<Int>(R.id.btnDemo).text = "Demo Mode"
    }

    private fun hasPermissions(): Boolean {
        return REQUIRED_PERMISSIONS.all { ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED }
    }

    private fun requestPermissions() {
        requestPermissions(REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        if (requestCode == REQUEST_CODE_PERMISSIONS) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                startService(Intent(this, AudioMonitoringService::class.java))
            } else {
                Toast.makeText(this, "Permissions denied", Toast.LENGTH_SHORT).show()
            }
        }
    }
}