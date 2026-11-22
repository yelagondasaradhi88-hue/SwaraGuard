package com.swaraguard.app.model

import com.google.gson.annotations.SerializedName

data class RiskAnalysis(
    @SerializedName("transcript") val transcript: String = "",
    @SerializedName("language_detected") val languageDetected: String = "en",
    @SerializedName("risk_score") val riskScore: Int = 0,
    @SerializedName("verdict") val verdict: String = "SAFE",
    @SerializedName("deepfake_voice_indicators") val deepfakeIndicators: List<String> = emptyList(),
    @SerializedName("scam_tactics_detected") val scamTactics: List<String> = emptyList(),
    @SerializedName("sensitive_info_leaked") val sensitiveInfoLeaked: Boolean = false,
    @SerializedName("leaked_items") val leakedItems: List<String> = emptyList(),
    @SerializedName("user_advice") val userAdvice: String = ""
) {
    enum class Verdict {
        SAFE, SUSPICIOUS, HIGH_RISK_SCAM, UNKNOWN;

        companion object {
            fun from(value: String): Verdict {
                return try {
                    valueOf(value)
                } catch (e: IllegalArgumentException) {
                    UNKNOWN
                }
            }
        }
    }

    enum class RiskLevel {
        LOW, MEDIUM, HIGH;

        companion object {
            fun fromScore(score: Int): RiskLevel {
                return when {
                    score >= 70 -> HIGH
                    score >= 40 -> MEDIUM
                    else -> LOW
                }
            }
        }
    }

    val riskLevel: RiskLevel get() = RiskLevel.fromScore(riskScore)
    val shouldInitiateProtection: Boolean
        get() = riskLevel == RiskLevel.HIGH ||
                (riskLevel == RiskLevel.MEDIUM && sensitiveInfoLeaked)

    val isDeepfakeDetected: Boolean
        get() = deepfakeIndicators.isNotEmpty() &&
                deepfakeIndicators[0] != "None detected"

    val hasScamTactics: Boolean
        get() = scamTactics.isNotEmpty() &&
                scamTactics[0] != "None"

    val hasSensitiveInfo: Boolean
        get() = sensitiveInfoLeaked && leakedItems.isNotEmpty()
}