package kr.ac.tukorea.nightsafety

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.PointF
import com.skt.tmap.TMapPoint
import com.skt.tmap.TMapView
import com.skt.tmap.TMapInsets
import com.skt.tmap.overlay.TMapMarkerItem
import com.skt.tmap.overlay.TMapPolyLine
import com.skt.tmap.overlay.TMapPolygon
import com.skt.tmap.poi.TMapPOIItem

class TmapPilotMap(
    context: Context,
    key: String,
    private var data: PilotData,
    private val onStatus: (String) -> Unit,
    private val onFacilities: (List<Facility>) -> Unit,
    private val onReady: () -> Unit,
    private val onLongPress: (GeoPoint) -> Unit
) {
    val view = TMapView(context)
    private var ready = false
    private var longPressHandled = false
    private var routeIndex = 0
    private var kinds = setOf("cctv", "bell", "police_osm_candidate", "lamp")
    private var location: GeoPoint? = null
    private var displayedLocation: GeoPoint? = null
    private var showWeak = false
    private var closed = false
    private var renderedRoutes: List<PilotRoute>? = null
    private var renderedRouteIndex = -1
    private var renderedWeak = false
    private var renderedEndpoints: List<Pair<String, GeoPoint>> = emptyList()
    private val endpointIcons = routePinIcons(context.resources.displayMetrics.density)
    private var visibleTop = 0
    private var visibleBottom = 0
    private var cameraOnRoute = true
    private val facilityOverlays = FacilityOverlayQueue(
        { work -> view.postOnAnimation { work() } }, ::removeFacility, ::addFacility)
    private val icons = FacilityClusterIcons(context)
    private var desiredGroups = emptyMap<String, FacilityCluster>()
    private val shownGroups = mutableMapOf<String, FacilityCluster>()
    private val recluster = Runnable { if (ready && !closed && view.width > 0) refreshFacilities() }

    private fun scheduleFacilities() {
        view.removeCallbacks(recluster)
        if (!closed) view.postDelayed(recluster, 120)
    }

    private fun refreshFacilities() {
        val facilities = data.mapFacilities(routeIndex, kinds)
        val groups = clusterFacilities(facilities, view.resources.displayMetrics.density.toDouble()) {
            view.getMapXForPoint(it.latitude, it.longitude).toDouble() to
                view.getMapYForPoint(it.latitude, it.longitude).toDouble()
        }
        desiredGroups = groups.associateBy { it.overlay.id }
        refreshShownClusters(shownGroups, desiredGroups)
        facilityOverlays.update(facilities.filter { it.polygon } + groups.map { it.overlay })
    }
    private val locationIcon = Bitmap.createBitmap(40, 40, Bitmap.Config.ARGB_8888).also { bitmap ->
        val canvas = Canvas(bitmap)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.WHITE }
        canvas.drawCircle(20f, 20f, 18f, paint)
        paint.color = Color.rgb(20, 90, 190)
        canvas.drawCircle(20f, 20f, 13f, paint)
    }

    init {
        view.addOnLayoutChangeListener { _, left, top, right, bottom, oldLeft, oldTop, oldRight, oldBottom ->
            if (right - left != oldRight - oldLeft || bottom - top != oldBottom - oldTop) {
                fitSelectedRoute(); scheduleFacilities()
            }
        }
        view.setOnApiKeyListenerCallback(object : TMapView.OnApiKeyListenerCallback {
            override fun onSKTMapApikeySucceed() { onStatus("TMAP 인증 성공 · 지도 준비 중") }
            override fun onSKTMapApikeyFailed(message: String?) { onStatus("TMAP 인증 실패 · 앱키와 앱 등록을 확인하거나 로컬 보기를 사용하세요") }
        })
        view.setOnMapReadyListener {
            if (closed) return@setOnMapReadyListener
            ready = true
            reset()
            update(routeIndex, kinds, location, showWeak)
            onReady()
        }
        view.setOnClickListenerCallback(object : TMapView.OnClickListenerCallback {
            override fun onPressDown(markers: ArrayList<TMapMarkerItem>?, pois: ArrayList<TMapPOIItem>?, point: TMapPoint?, screen: PointF?) { longPressHandled = false }
            override fun onPressUp(markers: ArrayList<TMapMarkerItem>?, pois: ArrayList<TMapPOIItem>?, point: TMapPoint?, screen: PointF?) {
                if (longPressHandled) return
                val id = markers?.firstOrNull()?.id ?: return
                shownGroups[id]?.let { onFacilities(it.members) }
            }
        })
        view.setOnLongClickListenerCallback(object : TMapView.OnLongClickListenerCallBack {
            override fun onLongPressEvent(markers: ArrayList<TMapMarkerItem>?, pois: ArrayList<TMapPOIItem>?, point: TMapPoint?) {
                if (closed || !ready || point == null) return
                longPressHandled = true
                view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                onLongPress(GeoPoint(point.latitude, point.longitude))
            }
        })
        view.setOnZoomChangedListener { scheduleFacilities() }
        view.setOnPanChangedListener { scheduleFacilities() }
        view.setOnRotationChangedListener { scheduleFacilities() }
        view.setSKTMapApiKey(key)
    }

    fun reset() {
        if (!ready) return
        // Vector SDK takes latitude first, unlike the Raster SDK center API.
        view.setCenterPoint(37.3465, 126.735)
        view.setZoomLevel(14)
    }

    fun replaceData(data: PilotData) { this.data = data }

    fun setVisibleArea(top: Int, bottom: Int) {
        if (visibleTop == top && visibleBottom == bottom) return
        visibleTop = top; visibleBottom = bottom
        fitSelectedRoute()
    }

    private fun fitSelectedRoute() {
        if (!ready || closed || !cameraOnRoute || view.width == 0 || view.height == 0) return
        val points = data.routes.getOrNull(routeIndex)?.points.orEmpty() + data.routeEndpoints(routeIndex).map { it.second }
        if (points.isEmpty()) return
        if (points.all { it == points.first() }) {
            view.setCenterPoint(points.first().latitude, points.first().longitude)
            view.setZoomLevel(16)
            return
        }
        val margin = minOf((52 * view.resources.displayMetrics.density).toInt(),
            (view.width - 1) / 2, (view.height - 1) / 2).coerceAtLeast(0)
        val room = view.height - visibleTop - visibleBottom
        val insets = TMapInsets(0, 0, 0, 0).apply {
            left = margin; right = margin
            // Very short views need fullscreen to show pins clear of all cards.
            top = if (room > margin) visibleTop else margin
            bottom = if (room > margin) visibleBottom else margin
        }
        view.fitBounds(view.getBoundsFromPoints(ArrayList(points.map { TMapPoint(it.latitude, it.longitude) })), insets)
    }

    fun close() { closed = true; view.removeCallbacks(recluster); facilityOverlays.cancel(); shownGroups.clear(); view.onDestroy() }

    private fun removeFacility(facility: Facility) {
        shownGroups.remove(facility.id)
        if (facility.polygon) view.removeTMapPolygon(facility.id)
        else view.removeTMapMarkerItem(facility.id)
    }

    private fun addFacility(facility: Facility) {
        if (facility.polygon) {
            val polygon = TMapPolygon(facility.id, ArrayList(facility.points.map { TMapPoint(it.latitude, it.longitude) }))
            polygon.setLineColor(facilityColor(facility.kind))
            polygon.setAreaColor(facilityColor(facility.kind))
            polygon.setAreaAlpha(70)
            view.addTMapPolygon(polygon)
        } else {
            val marker = TMapMarkerItem()
            marker.id = facility.id
            marker.setTMapPoint(facility.points.first().latitude, facility.points.first().longitude)
            marker.name = facility.title
            val group = desiredGroups.getValue(facility.id)
            marker.icon = icons.forMembers(group.members)
            shownGroups[facility.id] = group
            marker.setPosition(.5f, .5f)
            marker.setPriority(1.5f)
            marker.setCanShowCallout(false)
            view.addTMapMarkerItem(marker)
        }
    }

    fun update(selected: Int, visible: Set<String>, current: GeoPoint?, weak: Boolean = false) {
        routeIndex = selected; kinds = visible; location = current; showWeak = weak
        if (!ready || closed) return
        scheduleFacilities()
        val routeChanged = renderedRoutes !== data.routes || renderedRouteIndex != selected
        if (routeChanged) cameraOnRoute = current == null || current == displayedLocation
        if (routeChanged || renderedWeak != weak) {
            renderedRoutes = data.routes; renderedRouteIndex = selected; renderedWeak = weak
            view.removeAllTMapPolyLine()
            data.routes.indices.sortedBy { it == selected }.forEach { index ->
                val route = data.routes[index]
                if (route.points.size < 2) return@forEach
                // Vector SDK draws smaller priority values above larger values.
                if (index == selected) {
                    val border = TMapPolyLine("selected-route-border", ArrayList(route.points.map { TMapPoint(it.latitude, it.longitude) }))
                    border.setLineColor(Color.WHITE); border.setLineWidth(12f); border.setPriority(5f)
                    view.addTMapPolyLine(border)
                }
                val line = TMapPolyLine(route.id, ArrayList(route.points.map { TMapPoint(it.latitude, it.longitude) }))
                line.setLineColor(if (index == selected) Color.rgb(20, 90, 190) else Color.rgb(150, 160, 175))
                line.setLineWidth(if (index == selected) 8f else 3f)
                line.setLineAlpha(if (index == selected) 255 else 110)
                line.setOutLineColor(Color.WHITE)
                line.setOutLineWidth(0f)
                line.setPriority(if (index == selected) 4f else 9f)
                view.addTMapPolyLine(line)
            }
            data.routes.getOrNull(selected)?.segments?.filter { it.grade != "unknown" }?.forEachIndexed { index, segment ->
                val line = TMapPolyLine("grade-$index", ArrayList(segment.points.map { TMapPoint(it.latitude, it.longitude) }))
                line.setLineColor(segmentColor(segment.grade)); line.setLineWidth(4f)
                line.setOutLineWidth(0f); line.setPriority(3f)
                view.addTMapPolyLine(line)
            }
            if (weak && data.routes.isNotEmpty()) data.routes[selected].weakRanges.forEachIndexed { index, segment ->
                val line = TMapPolyLine("weak-$index", ArrayList(segment.points.map { TMapPoint(it.latitude, it.longitude) }))
                line.setLineColor(Color.rgb(205, 85, 15)); line.setLineWidth(6f); line.setPriority(2f)
                view.addTMapPolyLine(line)
            }
        }
        val endpoints = data.routeEndpoints(selected)
        if (endpoints != renderedEndpoints) {
            renderedEndpoints = endpoints
            view.removeTMapMarkerItem("route-endpoint-0")
            view.removeTMapMarkerItem("route-endpoint-1")
            endpoints.forEachIndexed { index, (label, point) ->
                val marker = TMapMarkerItem()
                marker.id = "route-endpoint-$index"
                marker.name = label
                marker.setTMapPoint(point.latitude, point.longitude)
                marker.icon = endpointIcons.getValue(label)
                marker.setPosition(.5f, 1f)
                marker.setPriority(1f)
                marker.setCanShowCallout(true)
                marker.calloutTitle = label
                marker.setCalloutSubTitle("입력한 위치 · 경로 연결 상태는 결과 패널을 확인하세요")
                view.addTMapMarkerItem(marker)
            }
        }
        if (routeChanged) fitSelectedRoute()
        current?.takeIf { it != displayedLocation }?.let {
            cameraOnRoute = false
            // SDK's tracking icon is uninitialized for one-shot location requests.
            view.removeTMapMarkerItem("current-location")
            val marker = TMapMarkerItem()
            marker.id = "current-location"
            marker.setTMapPoint(it.latitude, it.longitude)
            marker.icon = locationIcon
            marker.setPriority(0f)
            view.addTMapMarkerItem(marker)
            view.setCenterPoint(it.latitude, it.longitude)
            displayedLocation = it
        }
    }
}
