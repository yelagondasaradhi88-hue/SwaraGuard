package com.swaraguard.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class AudioDemoActivity : AppCompatActivity() {

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startActivity(Intent(this, AudioDemoActivity::class.java))
        } else {
            Toast.makeText(this, "Storage permission required", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_demo)

        findViewById<Button>(R.id.btnPlay).setOnClickListener {
            Toast.makeText(this, "Playing: Scam Call Detection", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnAnalyze).setOnClickListener {
            findViewById<Button>(R.id.btnAnalyze).text = "Analyzing..."
            findViewById<Button>(R.id.btnPlay).isEnabled = false
        }

        findViewById<Button>(R.id.btnBack).setOnClickListener {
            finish()
        }
    }
}