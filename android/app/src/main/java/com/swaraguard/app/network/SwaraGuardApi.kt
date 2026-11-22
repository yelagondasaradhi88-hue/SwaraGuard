package com.swaraguard.app.network

import com.swaraguard.app.model.RiskAnalysis
import com.swaraguard.app.model.ProtectionResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.http.*

interface SwaraGuardApi {

    @GET("/")
    fun getRoot(): Call<retrofit2.Response<String>>

    @GET("/health")
    fun healthCheck(): Call<HealthResponse>

    @POST("/api/analyze")
    fun analyzeAudio(
        @Multipart file: MultipartBody.Part
    ): Call<RiskAnalysis>

    @POST("/api/simulate-freeze")
    fun simulateFreeze(
        @Body request: FreezeRequest
    ): Call<ProtectionResponse>

    @POST("/api/protection-flow")
    fun initiateProtection(
        @Body request: ProtectionRequest
    ): Call<ProtectionResponse>

    @GET("/api/dashboard")
    fun getDashboard(
        @Query("user_id") userId: String? = null
    ): Call<DashboardResponse>

    @GET("/api/lock-status")
    fun getLockStatus(
        @Query("user_id") userId: String
    ): Call<LockStatusResponse>

    @GET("/api/deepfake-models")
    fun getDeepfakeModels(): Call<ModelListResponse>

    @GET("/api/scanners")
    fun getScanners(): Call<ScannerListResponse>

    @GET("/api/helpline")
    fun getHelpline(): Call<HelplineResponse>
}

// Request models
data class FreezeRequest(
    @SerializedName("account_alias") val accountAlias: String = "Primary Account (XXXX1234)",
    @SerializedName("reason") val reason: String = "Scam call detected",
    @SerializedName("duration_minutes") val durationMinutes: Int = 1440,
    @SerializedName("user_id") val userId: String? = null
)

data class ProtectionRequest(
    @SerializedName("account_alias") val accountAlias: String = "Primary Account (XXXX1234)",
    @SerializedName("reason") val reason: String = "Scam call - protection required",
    @SerializedName("user_phone") val userPhone: String? = null,
    @SerializedName("user_email") val userEmail: String? = null,
    @SerializedName("user_id") val userId: String? = null
)

// Response models
data class HealthResponse(
    @SerializedName("status") val status: String,
    @SerializedName("gemini_configured") val geminiConfigured: Boolean
)

data class DashboardResponse(
    @SerializedName("active_locks") val activeLocks: List<ActiveLock>,
    @SerializedName("total_safe_calls") val totalSafeCalls: Int
)

data class ActiveLock(
    @SerializedName("account_alias") val accountAlias: String,
    @SerializedName("locked_until") val lockedUntil: String,
    @SerializedName("expires_in") val expiresIn: Int,
    @SerializedName("status") val status: String
)

data class LockStatusResponse(
    @SerializedName("status") val status: String,
    @SerializedName("account_alias") val accountAlias: String? = null,
    @SerializedName("locked_until") val lockedUntil: String? = null
)

data class ModelListResponse(
    @SerializedName("models") val models: List<ModelInfo>
)

data class ModelInfo(
    @SerializedName("name") val name: String,
    @SerializedName("provider") val provider: String? = null
)

data class ScannerListResponse(
    @SerializedName("features") val features: List<ScannerFeature>
)

data class ScannerFeature(
    @SerializedName("name") val name: String,
    @SerializedName("enabled") val enabled: Boolean,
    @SerializedName("risk_levels") val riskLevels: List<String>
)

data class HelplineResponse(
    @SerializedName("primary") val primary: String,
    @SerializedName("description") val description: String
)

