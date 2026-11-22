package com.swaraguard.network

import com.swaraguard.models.RiskAnalysis
import com.swaraguard.models.AccountInfo
import com.swaraguard.models.UnifiedRisk
import retrofit2.Call
import retrofit2.http.*

interface SwaraGuardApi {

    @POST("/api/analyze-audio")
    fun analyzeAudio(
        @Part audio: MultipartBody.Part,
        @Query("session_id") sessionId: String = ""
    ): Call<RiskAnalysis>

    @POST("/api/transcript-analysis")
    fun analyzeTranscript(
        @Query("transcript_text") transcript: String
    ): Call<RiskAnalysis>

    @POST("/api/device-event")
    fun analyzeDeviceEvent(
        @Body request: DeviceEventRequest
    ): Call<DeviceRiskResponse>

    @POST("/api/risk-score")
    fun calculateRiskScore(
        @Body request: RiskScoreRequest
    ): Call<UnifiedRisk>

    @POST("/api/freeze-account")
    fun freezeAccount(
        @Body request: FreezeAccountRequest
    ): Call<FreezeAccountResponse>

    @POST("/api/transfer")
    fun transfer(
        @Body request: TransferRequest
    ): Call<TransferResponse>

    @GET("/api/account")
    fun getAccount(): Call<AccountInfo>

    @POST("/api/reset")
    fun reset(): Call<ResetResponse>

    @GET("/api/health")
    fun health(): Call<HealthResponse>
}

// Request/Response models
data class DeviceEventRequest(
    val session_id: String = "",
    val events: List<DeviceEvent> = emptyList()
)

data class DeviceRiskResponse(
    val device_risk_score: Double = 0.0,
    val risk_factors: List<String> = emptyList()
)

data class RiskScoreRequest(
    val voice_risk_score: Double = 0.0,
    val device_risk_score: Double = 0.0,
    val transaction_risk: Double = 0.0,
    val voice_signals: List<String> = emptyList(),
    val device_signals: List<String> = emptyList(),
    val transaction_signals: List<String> = emptyList()
)

data class FreezeAccountRequest(
    val account_alias: String = "XXXX1234",
    val reason: String = "High-risk scam detected",
    val duration_minutes: Int = 1440
)

data class FreezeAccountResponse(
    val status: String = "",
    val account_alias: String = ""
)

data class TransferRequest(
    val from_account: String = "XXXX1234",
    val to_beneficiary: String = "",
    val amount: Double = 0.0
)

data class TransferResponse(
    val success: Boolean = false,
    val message: String = ""
)

data class ResetResponse(
    val status: String = ""
)

data class HealthResponse(
    val status: String = ""
)

