# SwaraGuard AI - Android Phase 2 Architecture

## Overview
Phase 2 enables real-time call monitoring and automatic disconnection on Android devices when high-risk scams are detected.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Android App                                   │
├─────────────────────────────────────────────────────────────────────┤
│  CallScreeningService  ── listens for INCOMING_CALL              │
│  │                                                                  │
│  ├─► Query Gemini API with call transcript                        │
│  │                                                                  │
│  └─► Receive risk_score                                           │
│       │                                                             │
│       ├─ if risk_score < 60: ALLOW call                           │
│       ├─ if risk_score 60-79: WARN user                            │
│       └─ if risk_score >= 80: DISCONNECT + ALERT                    │
│                                                                  │
│  InCallService (foreground) ── shows live risk overlay          │
│  │                                                                  │
│  ├─ Real-time audio transcription                                  │
│  ├─ Live risk visualization                                        │
│  └─ Emergency action buttons                                       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
├─────────────────────────────────────────────────────────────────────┤
│  POST /api/analyze-audio                                            │
│  GET  /api/dashboard ── current risk scores                         │
│  POST /api/freeze-account ── emergency freeze                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. CallScreeningService (Kotlin)

```kotlin
class CallScreeningService : CallScreeningService() {

    override fun onScreenCall(callDetails: Call.Details) {
        val callerNumber = callDetails.handle.schemeSpecificPart

        // Step 1: Analyze caller
        CoroutineScope(Dispatchers.IO).launch {
            val analysis = analyzeCaller(callerNumber)

            val score = analysis.riskScore

            val response = if (score >= 80) {
                // HIGH RISK - Disconnect immediately
                respondToCall(CallResponse.Builder()
                    .setReject()
                    .setTriggerAlert()
                    .setDisconnect()
                    .build())

                // Send guardian alert
                sendGuardianAlert(analysis)

                // Auto-disconnect countdown
                startDisconnectTimer()

            } else if (score >= 60) {
                // MEDIUM RISK - Warn user
                respondToCall(CallResponse.Builder()
                    .setReject()
                    .setPreemptiveaelt("⚠️ Suspicious call detected")
                    .build())

            } else {
                // LOW RISK - Allow call
                respondToCall(CallResponse.Builder()
                    .setAllow()
                    .build())
            }
        }
    }

    private suspend fun analyzeCaller(phoneNumber: String): RiskAnalysis {
        // API call to backend
        val request = mapOf("caller_number" to phoneNumber)
        return apiService.analyzeCall(request)
    }
}
```

### 2. InCallService (Foreground Service)

```kotlin
@AndroidEntryPoint
class InCallService : Service() {

    private lateinit var notificationManager: NotificationManager
    private lateinit var audioRecorder: AudioRecord
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): InCallService = this@InCallService
    }

    override fun onCreate() {
        super.onCreate()
        startForeground(1001, createNotification())
        initializeAudioCapture()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Start capturing call audio
        startAudioCapture()

        // Poll backend every 3 seconds
        Handler(Looper.getMainLooper()).postDelayed({
            checkRiskAndUpdate()
        }, 3000)

        return START_STICKY
    }

    private fun startAudioCapture() {
        // Permission: android.permission.RECORD_AUDIO
        // Use CallScreeningService audio or AccessibilityService approach
        val sampleRate = 44100
        val bufferSize = AudioRecord.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )

        audioRecorder = AudioRecord(
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            bufferSize
        )

        audioRecorder.startRecording()
        startLiveAnalysis()
    }

    private fun startLiveAnalysis() {
        Thread {
            val buffer = ShortArray(1024)
            while (audioRecorder.recordingState == MediaRecorder.RecordingState.RECORDING) {
                val readSize = audioRecorder.read(buffer, 0, buffer.size)
                if (readSize > 0) {
                    // Send audio chunk to backend for analysis
                    val audioFile = saveAudioChunk(buffer)
                    val risk = analyzeWithBackend(audioFile)

                    // Update foreground notification
                    updateRiskDisplay(risk)

                    // Check for auto-disconnect
                    if (risk.score >= 80) {
                        triggerAutoDisconnect()
                    }
                }
            }
        }.start()
    }

    private fun triggerAutoDisconnect() {
        // Show 5-second countdown notification
        val countdownIntent = Intent(this, DisconnectCountdownActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
            putExtra("RISK_SCORE", 95)
        }

        // Schedule call end via TelephonyManager (requires system permission)
        // Or use AccessibilityService to simulate END_CALL press
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onDestroy() {
        audioRecorder.stop()
        audioRecorder.release()
        super.onDestroy()
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, "swaraguard_channel")
            .setContentTitle("SwaraGuard AI - Listening")
            .setContentText("Analyzing call for scams...")
            .setSmallIcon(R.drawable.ic_shield)
            .setOngoing(true)
            .build()
    }
}
```

### 3. DisconnectCountdownActivity (Full Screen)

```kotlin
class DisconnectCountdownActivity : AppCompatActivity() {

    private lateinit var countDownTimer: CountDownTimer
    private var remainingSeconds = 5

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Full-screen immersive mode for emergency
        window.setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        )

        setContentView(R.layout.activity_disconnect_countdown)

        val riskScore = intent.getIntExtra("RISK_SCORE", 95)

        // Display emergency UI
        setupEmergencyUI(riskScore)

        // Auto-disconnect countdown
        countDownTimer = object : CountDownTimer(5000, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                remainingSeconds = (millisUntilFinished / 1000).toInt()
                updateDisplay()
            }

            override fun onFinish() {
                // Execute disconnect
                executeCallDisconnect()

                // Show emergency contacts
                showEmergencyOptions()
            }
        }.start()
    }

    private fun executeCallDisconnect() {
        try {
            val telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager

            // Method 1: InCallScreeningService handles this automatically
            // Method 2: Use system call end (requires special permissions)

            Toast.makeText(this, "Call disconnected - Scam detected", Toast.LENGTH_LONG).show()

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun showEmergencyOptions() {
        val options = listOf(
            "Call 1930 (Cyber Crime Helpline)",
            "Report to cybercrime.gov.in",
            "Lock Bank Cards",
            "Change UPI PIN"
        )

        AlertDialog.Builder(this)
            .setTitle("After Scam Detected")
            .setItems(options.toTypedArray()) { _, which ->
                when (which) {
                    0 -> startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:1930")))
                    // Add other options...
                }
            }
            .show()
    }
}
```

## Required Android Permissions

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
<uses-permission android:name="android.permission.READ_CALL_LOG" />
<uses-permission android:name="android.permission.PROCESS_OUTGOING_CALLS" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.INTERNET" />

<!-- For auto-disconnect (system-level) -->
<uses-permission android:name="android.permission.DISCONNECT_PHONE_STATE" />
```

## Backend API Client (Kotlin)

```kotlin
interface SwaraGuardApiService {

    @POST("/api/analyze-audio")
    suspend fun analyzeAudio(
        @Header("Content-Type") contentType: String = "multipart/form-data",
        @Query("is_unknown_number") isUnknown: Boolean = false,
        @Part audioFile: MultipartBody.Part
    ): VoiceAnalysisResponse

    @POST("/api/guardian-alert")
    suspend fun sendGuardianAlert(
        @Body request: GuardianAlertRequest
    ): GuardianAlertResponse

    @POST("/api/freeze-account")
    suspend fun freezeAccount(
        @Body request: FreezeAccountRequest
    ): FreezeAccountResponse
}

data class VoiceAnalysisResponse(
    @SerializedName("voice_risk_score") val voiceRiskScore: Float,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("scam_intent") val scamIntent: ScamIntentResult,
    @SerializedName("deepfake") val deepfake: DeepfakeResult
)

data class ScamIntentResult(
    @SerializedName("scam_detected") val scamDetected: Boolean,
    @SerializedName("intent_categories") val intentCategories: List<String>,
    @SerializedName("confidence") val confidence: Float,
    @SerializedName("reasons") val reasons: List<String>
)
```

## Testing Strategy

1. **Unit Tests**: Test `CallScreeningService` with mock API responses
2. **Instrumentation Tests**: Test `InCallService` with test audio
3. **Manual Testing**: Use real calls with scam scripts

## Next Steps

1. Implement actual Gemini API integration for call transcription
2. Add deepfake detection model (ONNX or TensorFlow Lite)
3. Implement secure local storage for demo scenarios
4. Add accessibility service fallback for call end action