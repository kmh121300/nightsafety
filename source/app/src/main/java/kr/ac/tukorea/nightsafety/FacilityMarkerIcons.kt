package kr.ac.tukorea.nightsafety

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface

/** Both map renderers reuse the same density-scaled facility badges. */
internal fun facilityMarkerIcons(context: Context): Map<String, Bitmap> = mapOf(
    "cctv" to R.drawable.facility_cctv,
    "bell" to R.drawable.facility_bell,
    "lamp" to R.drawable.facility_lamp,
    "police_osm_candidate" to R.drawable.facility_police
).mapValues { (_, resource) ->
    val drawable = requireNotNull(context.getDrawable(resource))
    Bitmap.createBitmap(drawable.intrinsicWidth, drawable.intrinsicHeight, Bitmap.Config.ARGB_8888).also {
        drawable.setBounds(0, 0, it.width, it.height)
        drawable.draw(Canvas(it))
    }
}

internal fun facilityKindDrawableRes(kind: String): Int = when (kind) {
    "cctv" -> R.drawable.facility_cctv
    "bell" -> R.drawable.facility_bell
    "lamp" -> R.drawable.facility_lamp
    else -> R.drawable.facility_police
}

internal class FacilityClusterIcons(context: Context) {
    private val singles = facilityMarkerIcons(context)
    private val density = context.resources.displayMetrics.density
    private val badges = mutableMapOf<Pair<String, Int>, Bitmap>()

    fun forMembers(members: List<Facility>): Bitmap {
        val primaryKind = summarizeFacilityCluster(members).first().kind
        val base = singles.getValue(primaryKind)
        if (members.size == 1) return base
        return badges.getOrPut(primaryKind to members.size) {
            Bitmap.createBitmap((48 * density).toInt(), (36 * density).toInt(), Bitmap.Config.ARGB_8888).also {
                val canvas = Canvas(it)
                val paint = Paint(Paint.ANTI_ALIAS_FLAG)
                // Subtle stacked ring behind main icon to visually indicate multiple overlapping markers
                paint.color = Color.argb(65, 21, 51, 62)
                canvas.drawCircle(18f * density, 20f * density, 13.5f * density, paint)
                paint.color = Color.WHITE
                canvas.drawCircle(20f * density, 18f * density, 13f * density, paint)
                paint.color = facilityColor(primaryKind)
                paint.style = Paint.Style.STROKE
                paint.strokeWidth = 1.4f * density
                canvas.drawCircle(20f * density, 18f * density, 12.2f * density, paint)
                paint.style = Paint.Style.FILL

                canvas.drawBitmap(base, 4 * density, 6 * density, null)
                canvas.scale(density, density)

                // Pill-shaped count badge at top-right
                paint.color = Color.WHITE
                canvas.drawRoundRect(21f, 0f, 48f, 20f, 10f, 10f, paint)
                paint.color = Color.rgb(8, 127, 120)
                canvas.drawRoundRect(22.5f, 1.5f, 46.5f, 18.5f, 8.5f, 8.5f, paint)
                paint.color = Color.WHITE
                paint.typeface = Typeface.DEFAULT_BOLD
                paint.textSize = 10.5f
                paint.textAlign = Paint.Align.CENTER
                val label = "+${members.size}"
                // Fit exact counts even when many co-located records share one badge.
                paint.textSize *= minOf(1f, 21f / paint.measureText(label))
                canvas.drawText(label, 34.5f, (20f - paint.fontMetrics.ascent - paint.fontMetrics.descent) / 2, paint)
            }
        }
    }
}
