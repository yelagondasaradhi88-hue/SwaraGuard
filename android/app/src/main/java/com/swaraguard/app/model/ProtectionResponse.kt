package com.swaraguard.app.model

import com.google.gson.annotations.SerializedName
import java.time.Instant

data class ProtectionResponse(
    @SerializedName("status") val status: String = "",
    @SerializedName("freeze_status") val freezeStatus: String = "",
    @SerializedName("freeze_expires") val freezeExpires: String = "",
    @SerializedName("account_alias") val accountAlias: String = "",
    @SerializedName("reason") val reason: String = "",
    @SerializedName("duration_minutes") val durationMinutes: Int = 1440,
    @SerializedName("helpline_1930") val helpline1930: String = "1930",
    @SerializedName("next_steps") val nextSteps: List<String> = emptyList(),
    @SerializedName("action_1930_dial") val action1930Dial: String = "tel:1930",
    @SerializedName("sms_template") val smsTemplate: String = "",
    @SerializedName("dashboard_url") val dashboardUrl: String = "",
    @SerializedName("bank_app_urls") val bankAppUrls: List<String> = emptyList()
) {
    var remainingMinutes: Int = 1440
        private set

    constructor(status: String, expires: String, minutes: Int) : this() {
        this.status = status
        this.freezeExpires = expires
        this.remainingMinutes = minutes
    }

    fun isStillActive(): Boolean {
        try {
            val expires = Instant.parse(freezeExpires)
            val now = Instant.now()
            return now.isBefore(expires)
        } catch (e: Exception) {
            return true
        }
    }

    fun getSecondsRemaining(): Long {
        return (remainingMinutes * 60L)
    }
}