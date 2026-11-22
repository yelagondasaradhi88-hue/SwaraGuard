package com.swaraguard.models

import com.google.gson.annotations.SerializedName

data class RiskAnalysis(
    @SerializedName("voice_risk_score") val voiceRiskScore: Double = 0.0,
    @SerializedName("risk_level") val riskLevel: String = "LOW",
    @SerializedName("transcript") val transcript: String = "",
    @SerializedName("deepfake_probability") val deepfakeProb: Double = 0.0,
    @SerializedName("is_mock") val isMock: Boolean = true
)

data class DeviceEvent(
    val eventType: String,
    val description: String,
    val riskPoints: Int = 0
)

data class UnifiedRisk(
    val score: Int = 0,
    val level: String = "LOW",
    val signals: List<String> = emptyList()
)

data class AccountInfo(
    val status: String,
    val balance: Double
)