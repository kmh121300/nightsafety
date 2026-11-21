package kr.ac.tukorea.nightsafety

import android.content.Context
import android.graphics.Canvas
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.Typeface
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import android.view.GestureDetector
import android.view.HapticFeedbackConstants
import android.view.View
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.hypot

fun segmentColor(grade: String): Int = when (grade) {
    "normal" -> Color.rgb(28, 125, 80)
    "caution" -> Color.rgb(170, 105, 0)
    "vulnerable" -> Color.rgb(165, 45, 55)
    else -> Color.rgb(132, 150, 171)
}

internal fun routePinIcons(density: Float): Map<String, Bitmap> = mapOf(
    "출발" to Color.rgb(8, 127, 91), "도착" to Color.rgb(190, 55, 65),
    "출발·도착" to Color.rgb(20, 90, 190)
).mapValues { (label, color) ->
    Bitmap.createBitmap((88 * density).toInt(), (44 * density).toInt(), Bitmap.Config.ARGB_8888).also { bitmap ->
        val canvas = Canvas(bitmap)
        canvas.scale(density, density)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG)
        val tail = Path().apply { moveTo(34f, 30f); lineTo(54f, 30f); lineTo(44f, 44f); close() }
        paint.color = Color.WHITE
        canvas.drawPath(tail, paint)
        canvas.drawRoundRect(0f, 0f, 88f, 34f, 12f, 12f, paint)
        paint.color = color
        canvas.drawRoundRect(2f, 2f, 86f, 32f, 10f, 10f, paint)
        val inner = Path().apply { moveTo(37f, 30f); lineTo(51f, 30f); lineTo(44f, 40f); close() }
        canvas.drawPath(inner, paint)
        paint.color = Color.WHITE; paint.textSize = 12f
        paint.typeface = Typeface.DEFAULT_BOLD; paint.textAlign = Paint.Align.CENTER
        canvas.drawText(label, 44f, (34f - paint.fontMetrics.ascent - paint.fontMetrics.descent) / 2, paint)
    }
}

/** Local geographic geometry only; no background map or inferred connectors. */
class PilotPreviewView(context: Context) : View(context) {
    var data: PilotData? = null
    var selectedRoute = 0
    var visibleKinds = setOf("cctv", "bell", "police_osm_candidate", "lamp")
    var currentLocation: GeoPoint? = null
    var showWeak = false
    var onFacilitiesClick: (List<Facility>) -> Unit = {}
    var onMapLongPress: (GeoPoint) -> Unit = {}
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val linePath = Path()
    private var zoom = 1f
    private var panX = 0f
    private var panY = 0f
    private var downX = 0f
    private var downY = 0f
    private var lastX = 0f
    private var lastY = 0f
    private var moved = false
    private var longPressed = false
    private val density = resources.displayMetrics.density
    private val endpointIcons = routePinIcons(density)
    private val facilityIcons = FacilityClusterIcons(context)
    private var clusteredFacilities: List<Facility>? = null
    private var clusteredFit = Double.NaN
    private var clusteredZoom = Float.NaN
    private var clusteredWidth = 0
    private var clusteredHeight = 0
    private var facilityGroups = emptyList<FacilityCluster>()

    private fun groups(fit: Double): List<FacilityCluster> {
        val facilities = data?.mapFacilities(selectedRoute, visibleKinds) ?: return emptyList()
        if (facilities !== clusteredFacilities || fit != clusteredFit || zoom != clusteredZoom ||
            width != clusteredWidth || height != clusteredHeight) {
            facilityGroups = clusterFacilities(facilities, density.toDouble()) {
                (projectX(it.longitude, fit) - panX).toDouble() to (projectY(it.latitude, fit) - panY).toDouble()
            }
            clusteredFacilities = facilities; clusteredFit = fit; clusteredZoom = zoom
            clusteredWidth = width; clusteredHeight = height
        }
        return facilityGroups
    }
    private val metersPerDegree = 111_195.0
    private val longitudeScale = cos(Math.toRadians(37.3465))
    private val spanX = .032 * longitudeScale * metersPerDegree
    private val spanY = .025 * metersPerDegree
    private val scale = ScaleGestureDetector(context, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
        override fun onScale(detector: ScaleGestureDetector): Boolean {
            zoom = (zoom * detector.scaleFactor).coerceIn(1f, 8f)
            moved = true
            invalidate()
            return true
        }
    })
    private val gestures = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(event: MotionEvent): Boolean = true
        override fun onLongPress(event: MotionEvent) {
            val fit = fitScale() * zoom
            if (data == null || moved || scale.isInProgress || fit <= 0) return
            longPressed = true
            performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            onMapLongPress(GeoPoint(
                37.3465 - (event.y - height / 2 - panY) / (metersPerDegree * fit),
                126.735 + (event.x - width / 2 - panX) / (longitudeScale * metersPerDegree * fit)))
        }
    })

    init {
        contentDescription = "배경지도 없는 실제 좌표 미리보기. 손가락으로 이동하고 두 손가락으로 확대합니다. 시설을 누르면 상세 정보를 표시합니다."
        isClickable = true
    }

    fun reset() { zoom = 1f; panX = 0f; panY = 0f; invalidate() }

    private fun fitScale(): Double = minOf((width - 40 * density) / spanX, (height - 48 * density) / spanY)

    private fun projectX(longitude: Double, fit: Double): Float =
        (width / 2 + (longitude - 126.735) * longitudeScale * metersPerDegree * fit * zoom + panX).toFloat()

    private fun projectY(latitude: Double, fit: Double): Float =
        (height / 2 - (latitude - 37.3465) * metersPerDegree * fit * zoom + panY).toFloat()

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawColor(Color.rgb(232, 238, 243))
        paint.color = Color.rgb(213, 223, 232)
        paint.strokeWidth = density
        for (i in 1..5) {
            canvas.drawLine(width * i / 6f, 0f, width * i / 6f, height.toFloat(), paint)
            canvas.drawLine(0f, height * i / 6f, width.toFloat(), height * i / 6f, paint)
        }
        val data = data ?: return
        val fit = fitScale()
        data.mapFacilities(selectedRoute, visibleKinds).filter { it.polygon }.forEach { facility ->
            paint.color = facilityColor(facility.kind); paint.alpha = 180
            drawLine(canvas, facility.points, 2 * density, fit)
        }
        paint.alpha = 255
        data.routes.indices.sortedBy { it == selectedRoute }.forEach { index ->
            if (index == selectedRoute) {
                paint.color = Color.WHITE
                drawLine(canvas, data.routes[index].points, 8f * density, fit)
            }
            paint.color = if (index == selectedRoute) Color.rgb(20, 90, 190) else Color.argb(110, 150, 160, 175)
            drawLine(canvas, data.routes[index].points, (if (index == selectedRoute) 5f else 2f) * density, fit)
        }
        data.routes.getOrNull(selectedRoute)?.segments?.filter { it.grade != "unknown" }?.forEach {
            paint.color = segmentColor(it.grade)
            drawLine(canvas, it.points, 2 * density, fit)
        }
        if (showWeak && data.routes.isNotEmpty()) {
            paint.color = Color.rgb(205, 85, 15)
            data.routes[selectedRoute].weakRanges.forEach { drawLine(canvas, it.points, 3 * density, fit) }
        }
        groups(fit).forEach { group ->
            val icon = facilityIcons.forMembers(group.members)
            canvas.drawBitmap(icon, group.x.toFloat() + panX - icon.width / 2f,
                group.y.toFloat() + panY - icon.height / 2f, null)
        }
        data.routeEndpoints(selectedRoute).forEach { (label, point) ->
            val icon = endpointIcons.getValue(label)
            canvas.drawBitmap(icon, projectX(point.longitude, fit) - icon.width / 2,
                projectY(point.latitude, fit) - icon.height, null)
        }
        currentLocation?.let {
            paint.color = Color.MAGENTA
            canvas.drawCircle(projectX(it.longitude, fit), projectY(it.latitude, fit), 6 * density, paint)
        }
        paint.color = Color.rgb(65, 87, 108)
        paint.textSize = 11 * density
        canvas.drawText("실제 좌표 미리보기 · 배경지도 없음", 8 * density, 17 * density, paint)
    }

    private fun drawLine(canvas: Canvas, points: List<GeoPoint>, width: Float, fit: Double) {
        linePath.reset()
        points.forEachIndexed { index, point ->
            val px = projectX(point.longitude, fit)
            val py = projectY(point.latitude, fit)
            if (index == 0) linePath.moveTo(px, py) else linePath.lineTo(px, py)
        }
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = width
        paint.strokeJoin = Paint.Join.ROUND
        paint.strokeCap = Paint.Cap.ROUND
        canvas.drawPath(linePath, paint)
        paint.style = Paint.Style.FILL
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        scale.onTouchEvent(event)
        gestures.onTouchEvent(event)
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downX = event.x; downY = event.y; lastX = event.x; lastY = event.y; moved = false; longPressed = false
                parent.requestDisallowInterceptTouchEvent(true)
            }
            MotionEvent.ACTION_MOVE -> {
                if (abs(event.x - downX) + abs(event.y - downY) > 10 * density) moved = true
                if (!longPressed && !scale.isInProgress && event.pointerCount == 1) {
                    panX += event.x - lastX; panY += event.y - lastY; invalidate()
                }
                lastX = event.x; lastY = event.y
            }
            MotionEvent.ACTION_UP -> {
                if (!moved && !longPressed) {
                    performClick()
                    val fit = fitScale()
                    val group = groups(fit).firstOrNull {
                        abs(it.x + panX - event.x) <= it.widthDp * density / 2 &&
                            abs(it.y + panY - event.y) <= it.heightDp * density / 2
                    }
                    if (group != null) onFacilitiesClick(group.members)
                    else data?.mapFacilities(selectedRoute, visibleKinds)?.filter { it.polygon }
                        ?.minByOrNull { facility -> facility.points.minOf { p ->
                            hypot(projectX(p.longitude, fit) - event.x, projectY(p.latitude, fit) - event.y)
                        } }?.let { facility ->
                            if (facility.points.minOf { p -> hypot(projectX(p.longitude, fit) - event.x,
                                    projectY(p.latitude, fit) - event.y) } <= 24 * density) onFacilitiesClick(listOf(facility))
                        }
                }
                parent.requestDisallowInterceptTouchEvent(false)
            }
            MotionEvent.ACTION_CANCEL -> parent.requestDisallowInterceptTouchEvent(false)
        }
        return true
    }

    override fun performClick(): Boolean { super.performClick(); return true }
}

fun facilityColor(kind: String): Int = when (kind) {
    "cctv" -> Color.rgb(32, 115, 170)
    "bell" -> Color.rgb(195, 91, 21)
    "lamp" -> Color.rgb(148, 111, 0)
    else -> Color.rgb(103, 63, 155)
}
