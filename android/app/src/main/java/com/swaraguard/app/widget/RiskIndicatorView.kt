package com.swaraguard.app.widget

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.RectF
import android.util.AttributeSet
import android.view.View
import androidx.core.content.ContextCompat
import com.swaraguard.app.R
import kotlin.math.min

class RiskIndicatorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var textPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    private var currentScore = 0
    private var currentLevel = RiskLevel.LOW

    private var centerX = 0f
    private var centerY = 0f
    private var radius = 0f

    enum class RiskLevel(val color: Int) {
        LOW(R.color.risk_low),
        MEDIUM(R.color.risk_medium),
        HIGH(R.color.risk_high)
    }

    fun setRiskLevel(score: Int, level: RiskLevel? = null) {
        currentScore = score.coerceIn(0, 100)
        currentLevel = level ?: when {
            currentScore >= 70 -> RiskLevel.HIGH
            currentScore >= 40 -> RiskLevel.MEDIUM
            else -> RiskLevel.LOW
        }
        invalidate()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val size = min(measureDimension(widthMeasureSpec), measureDimension(heightMeasureSpec))
        setMeasuredDimension(size, size)
    }

    private fun measureDimension(measureSpec: Int): Int {
        val specMode = MeasureSpec.getMode(measureSpec)
        val specSize = MeasureSpec.getSize(measureSpec)
        val desiredSize = 300 // Default size

        return when (specMode) {
            MeasureSpec.EXACTLY -> specSize
            MeasureSpec.AT_MOST -> min(desiredSize, specSize)
            else -> desiredSize
        }
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        centerX = w / 2f
        centerY = h / 2f
        radius = min(w, h) / 2f * 0.8f

        setupPaints()
    }

    private fun setupPaints() {
        // Background paint
        backgroundPaint.style = Paint.Style.FILL
        backgroundPaint.color = ContextCompat.getColor(context, R.color.surface)

        // Arc paint
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = 12f
        paint.isAntiAlias = true

        // Text paint
        textPaint.textSize = 48f * resources.displayMetrics.scaledDensity
        textPaint.isAntiAlias = true
        textPaint.textAlign = Paint.Align.CENTER
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // Draw outer circle background
        canvas.drawCircle(centerX, centerY, radius, backgroundPaint)

        // Draw risk arc
        drawRiskArc(canvas)

        // Draw score
        drawScore(canvas)

        // Draw level label
        drawLevel(canvas)
    }

    private fun drawRiskArc(canvas: Canvas) {
        val arcPaint = paint
        arcPaint.color = ContextCompat.getColor(context, currentLevel.color)
        arcPaint.strokeWidth = 16f

        val rect = RectF(
            centerX - radius + 8,
            centerY - radius + 8,
            centerX + radius - 8,
            centerY + radius - 8
        )

        val sweepAngle = (currentScore / 100f) * 360f
        canvas.drawArc(rect, -90f, sweepAngle, false, arcPaint)
    }

    private fun drawScore(canvas: Canvas) {
        val scoreText = "$currentScore$"
        textPaint.color = ContextCompat.getColor(context, android.R.color.black)
        canvas.drawText(scoreText, centerX, centerY + textPaint.textSize / 4)
    }

    private fun drawLevel(canvas: Canvas) {
        val levelText = currentLevel.name
        textPaint.color = ContextCompat.getColor(context, R.color.onSurfaceVariant)
        textPaint.textSize = 14f * resources.displayMetrics.scaledDensity

        // Draw below the circle
        canvas.drawText(levelText, centerX, centerY + radius + 30f)
    }
}