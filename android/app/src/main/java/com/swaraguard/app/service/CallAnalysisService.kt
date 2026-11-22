package com.swaraguard.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import com.swaraguard.app.R
import com.swaraguard.app.model.RiskAnalysis
import com.swaraguard.app.network.ApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.concurrent.Executors

class CallAnalysisService : Service() {

    companion object {
        const val CHANNEL_ID = "call_analysis_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_END_CALL = "com.swaraguard.END_CALL"
        const val ACTION_STOP = "com.swaraguard.STOP"

        const val CHUNK_DURATION_MS = 4000L  // 3-5 seconds chunks
        const val MAX_CALL_DURATION_MS = 120000L  // 2 minutes max
        const val SAMPLE_RATE = 44100
        private const val TAG = "CallAnalysisService"
    }

    private var isRunning = false
    private var currentJob: Job? = null
    private var startTimeMs: Long = 0

    private val executor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private val scope = CoroutineScope(Dispatchers.Main + Job())

    private var audioRecord: AudioRecord? = null
    private var tempDir: File? = null
    private var currentChunkFile: File? = null

    // Risk state
    private var currentRiskAnalysis: RiskAnalysis? = null
    private var riskCallback: RiskCallback? = null

    interface RiskCallback {
        fun onRiskUpdate(analysis: RiskAnalysis)
        fun onHighRiskDetected(analysis: RiskAnalysis)
        fun onCallEnded()
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        tempDir = createTempDir()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_END_CALL -> {
                forceEndCall()
            }
            ACTION_STOP -> {
                stopSelf()
            }
            null -> {
                // Start analysis
                startAnalysis()
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        currentJob?.cancel()
        executor.shutdown()
        audioRecord?.release()
        currentChunkFile?.delete()
        tempDir?.delete()
    }

    fun setRiskCallback(callback: RiskCallback) {
        riskCallback = callback
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "SwaraGuard Call Analysis",
                NotificationManager.IMPORTANCE_LOW
            )
            channel.description = "Analyzing call for scam detection"
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(isScanning: Boolean = true, riskScore: Int = 0): Notification {
        val title = if (isScanning) {
            "SwaraGuard - Scanning Call"
        } else {
            "SwaraGuard - Risk Detected"
        }

        val scoreText = if (riskScore > 0) "Risk: $riskScore%" else ""

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(scoreText.ifEmpty { "Listening for scam patterns..." })
            .setSmallIcon(R.drawable.ic_monitor_24dp)
            .setOngoing(isScanning)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun startAnalysis() {
        if (isRunning) return

        isRunning = true
        startTimeMs = System.currentTimeMillis()

        startForeground(NOTIFICATION_ID, createNotification())

        // Start audio recording from speakerphone/mic
        startAudioRecording()

        scope.launch {
            delay(MAX_CALL_DURATION_MS)
            stopAnalysis()
        }
    }

    private fun startAudioRecording() {
        try {
            val bufferSize = AudioRecord.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )

            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize
            )

            audioRecord?.startRecording()

            // Start chunking in background
            executor.execute { processAudioChunks() }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting audio recording", e)
        }
    }

    private fun processAudioChunks() {
        val apiService = ApiClient.createService()

        while (isRunning) {
            val elapsed = System.currentTimeMillis() - startTimeMs
            if (elapsed >= MAX_CALL_DURATION_MS) {
                break
            }

            // Create 3-5 second chunk
            val chunkStart = System.currentTimeMillis()
            val chunkFile = createChunkFile()

            try {
                val buffer = ShortArray(bufferSize / 2)
                val recordedBytes = mutableListOf<Byte>()

                val chunkStartMs = System.currentTimeMillis()
                while (System.currentTimeMillis() - chunkStartMs < CHUNK_DURATION_MS) {
                    val readSize = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (readSize > 0) {
                        for (i in 0 until readSize) {
                            val value = buffer[i]
                            recordedBytes.add((value and 0xFF).toByte())
                            recordedBytes.add(((value shr 8) and 0xFF).toByte())
                        }
                    }
                }

                writeChunkFile(chunkFile, recordedBytes.toByteArray())

                // Analyze chunk
                val analysis = analyzeChunk(apiService, chunkFile)

                mainHandler.post {
                    handleAnalysisResult(analysis)
                }

                currentChunkFile?.delete()

            } catch (e: Exception) {
                Log.e(TAG, "Error processing chunk", e)
            }

            delay(CHUNK_DURATION_MS + 500) // 500ms gap between chunks
        }
    }

    private fun createChunkFile(): File {
        val file = File(tempDir, "chunk_${System.currentTimeMillis()}.wav")
        if (!file.exists()) {
            file.createNewFile()
        }
        return file
    }

    private fun writeChunkFile(file: File, data: ByteArray) {
        FileOutputStream(file).use { out ->
            // Write WAV header
            val sampleRate = SAMPLE_RATE
            val numChannels = 1
            val bitsPerSample = 16
            val byteRate = sampleRate * numChannels * bitsPerSample / 8
            val blockAlign = numChannels * bitsPerSample / 8
            val dataLength = data.size

            val header = byteArrayOf(
                'R'.code.toByte(), 'W'.code.toByte(), 'A'.code.toByte(), 'V'.code.toByte(),
                (dataLength + 36).toByteArrayInt(),
                'W'.code.toByte(), 'A'.code.toByte(), 'V'.code.toByte(), 'E'.code.toByte(),
                (36).toByteArrayInt(), // Subchunk2Size - 36
                (dataLength).toByteArrayInt() // Subchunk2Size
            )
            out.write(header)
            out.write(data)
        }
    }

    private fun ByteArray.toByteArrayInt(): ByteArray {
        val bytes = ByteArray(4)
        for (i in 0..3) {
            bytes[i] = this[i]
        }
        return bytes
    }

    private suspend fun analyzeChunk(
        apiService: com.swaraguard.app.network.SwaraGuardApi,
        file: File
    ): RiskAnalysis? = kotlinx.coroutines.withContext(Dispatchers.IO) {
        try {
            val requestBody = file.asRequestBody("audio/wav".toMediaTypeOrNull())
            val multipart = MultipartBody.Part.createFormData("file", file.name, requestBody)

            val response = apiService.analyzeAudio(multipart).execute()
            if (response.isSuccessful) {
                response.body()
            } else {
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Analysis error", e)
            null
        }
    }

    private fun handleAnalysisResult(analysis: RiskAnalysis?) {
        if (analysis == null) return

        currentRiskAnalysis = analysis
        val riskScore = analysis.riskScore

        // Update notification
        val notification = createNotification(
            isScanning = analysis.riskLevel != RiskAnalysis.RiskLevel.HIGH,
            riskScore = riskScore
        )
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)

        // Notify callback
        riskCallback?.onRiskUpdate(analysis)

        if (analysis.riskLevel == RiskAnalysis.RiskLevel.HIGH) {
            riskCallback?.onHighRiskDetected(analysis)
        }
    }

    private fun stopAnalysis() {
        isRunning = false

        // Process remaining audio
        currentChunkFile?.delete()

        // Update notification
        val notification = createNotification(isScanning = false)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)

        // Send completion
        mainHandler.post {
            riskCallback?.onCallEnded()
            stopSelf()
        }
    }

    private fun forceEndCall() {
        Log.d(TAG, "Force ending call")

        // This would use TelecomManager.endCall() on actual device
        // For now, just stop analysis
        stopAnalysis()
    }

    private fun delay(ms: Long) {
        Thread.sleep(ms)
    }
}