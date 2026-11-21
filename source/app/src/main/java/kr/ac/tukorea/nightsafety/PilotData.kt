package kr.ac.tukorea.nightsafety

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

data class GeoPoint(val latitude: Double, val longitude: Double)

data class Facility(
    val id: String,
    val kind: String,
    val points: List<GeoPoint>,
    val polygon: Boolean,
    val dataAsOf: String?,
    val title: String,
    val detail: String
)

data class PilotRoute(
    val id: String,
    val title: String,
    val distanceMeters: Double,
    val pedestrianPercent: Double,
    val points: List<GeoPoint>,
    val durationSeconds: Double? = null,
    val routeStatus: String = "incomplete",
    val availableDataScore: Double? = null,
    val scoreStatus: String = "unavailable",
    val basisTypes: List<String> = emptyList(),
    val segments: List<RouteSegment> = emptyList(),
    val edgeReferences: List<String> = emptyList(),
    val profiles: List<String> = emptyList(),
    val weakRanges: List<RouteSegment> = emptyList(),
    val safetyScore: Double? = null,
    val averageSafety: Double? = null,
    val weakSafety: Double? = null,
    val facilityCounts: Map<String, Int?> = emptyMap()
) {
    val estimatedMinutes: Double get() = (durationSeconds ?: (distanceMeters / 1.2)) / 60
}

data class RouteSegment(val lengthMeters: Double, val score: Double?, val grade: String, val points: List<GeoPoint>)

data class PilotData(
    val facilities: List<Facility>,
    val routes: List<PilotRoute>,
    val destination: GeoPoint,
    val exitGapMeters: Double,
    val complete: Boolean,
    val safetyScore: Double?,
    val origin: GeoPoint? = null,
    val snapshotJson: String? = null,
    val versions: Map<String, String> = emptyMap(),
    val sourceSummary: String = "고정된 실험 경로",
    val savedSnapshot: Boolean = false,
    val missingTypes: List<String> = emptyList()
) {
    val facilitiesById: Map<String, Facility> = facilities.associateBy { it.id }
    @Transient private var cachedVisibleKinds: Set<String>? = null
    @Transient private var cachedVisibleList: List<Facility>? = null
    @Transient private var cachedMapRoute: PilotRoute? = null
    @Transient private var cachedNearby: List<Facility> = emptyList()
    @Transient private var cachedMapKinds: Set<String>? = null
    @Transient private var cachedMapList: List<Facility> = emptyList()

    fun mapFacilities(selected: Int, kinds: Set<String>): List<Facility> {
        val route = routes.getOrNull(selected)
        if (route !== cachedMapRoute) {
            cachedMapRoute = route
            cachedNearby = facilitiesNearRoute(facilities, route?.points.orEmpty())
            cachedMapKinds = null
        }
        if (kinds == cachedMapKinds) return cachedMapList
        return cachedNearby.filter { it.kind in kinds }.also {
            cachedMapKinds = kinds.toSet()
            cachedMapList = it
        }
    }

    fun visibleFacilities(kinds: Set<String>): List<Facility> {
        if (kinds == cachedVisibleKinds) cachedVisibleList?.let { return it }
        return facilities.filter { it.kind in kinds }.also {
            cachedVisibleKinds = kinds
            cachedVisibleList = it
        }
    }

    companion object {
        fun parse(facilitiesJson: String, routesJson: String, geometryJson: String, securityLightsJson: String? = null): PilotData = try {
            val root = JSONObject(facilitiesJson)
            require(root.getString("type") == "FeatureCollection") { "시설 GeoJSON 형식 오류" }
            val lights = securityLightsJson?.let { json ->
                JSONObject(json).also { require(it.getString("type") == "FeatureCollection") }.getJSONArray("features").objects()
            } ?: emptyList()
            val facilities = (root.getJSONArray("features").objects() + lights).map { feature ->
                val properties = feature.getJSONObject("properties")
                val geometry = feature.getJSONObject("geometry")
                val kind = properties.getString("kind")
                require(kind in setOf("cctv", "bell", "lamp", "police_osm_candidate")) { "알 수 없는 시설 유형" }
                val polygon = geometry.getString("type") == "Polygon"
                require(polygon || geometry.getString("type") == "Point") { "지원하지 않는 시설 도형" }
                val coords = geometry.getJSONArray("coordinates")
                val points = if (polygon) coords.getJSONArray(0).points() else listOf(coords.point())
                require(points.isNotEmpty()) { "시설 좌표 없음" }
                val label = when (kind) { "cctv" -> "CCTV"; "bell" -> "비상벨"; "lamp" -> "보안등"; else -> "경찰시설 후보" }
                val sourceId = if (properties.has("csv_row")) properties.getInt("csv_row").toString()
                    else "${properties.getString("osm_type")}:${properties.getString("osm_id")}"
                Facility(
                    properties.optString("facility_id").ifBlank { "$kind:$sourceId" }, kind, points, polygon,
                    properties.optString("data_as_of").takeIf { it.isNotBlank() },
                    "$label · ${facilityAddress(properties) ?: "주소 정보 없음"}"
                        .let { if (kind == "police_osm_candidate") "$it · OSM 후보" else it },
                    facilityDetail(properties, kind, points.first().takeUnless { polygon })
                )
            }
            val seenIds = HashSet<String>(facilities.size)
            require(facilities.all { seenIds.add(it.id) }) { "시설 식별자 중복" }
            val result = JSONObject(routesJson)
            require(result.getString("status") == "route_incomplete" && !result.getBoolean("safety_scored")) {
                "현재 파일럿은 미완결·점수 미산출 자료만 지원합니다"
            }
            val geometry = JSONObject(geometryJson)
            require(geometry.getString("type") == "FeatureCollection")
            val featuresByRoute = geometry.getJSONArray("features").objects().groupBy {
                it.getJSONObject("properties").getString("route")
            }
            val routes = listOf("distance_only" to "거리 우선", "pedestrian_preferred" to "보행선 우선").map { (id, title) ->
                val route = result.getJSONObject("routes").getJSONObject(id)
                val segments = route.getJSONArray("segments").objects()
                val lines = featuresByRoute[id] ?: emptyList()
                require(lines.size == segments.size && lines.isNotEmpty()) { "경로 선형과 계산 결과 불일치" }
                val points = mutableListOf<GeoPoint>()
                lines.forEachIndexed { index, feature ->
                    val line = feature.getJSONObject("geometry")
                    require(line.getString("type") == "LineString")
                    val pair = line.getJSONArray("coordinates").points()
                    val properties = feature.getJSONObject("properties")
                    require(pair.size == 2) { "경로 간선 좌표 오류" }
                    for (field in listOf("from", "to", "way")) {
                        require(properties.getLong(field) == segments[index].getLong(field)) { "경로 원본 간선 불일치" }
                    }
                    if (index == 0) points.add(pair.first())
                    else require(points.last() == pair.first()) { "경로 단절: 연결선을 임의 생성하지 않습니다" }
                    points.add(pair.last())
                }
                val distance = route.getDouble("distance_m")
                val share = route.getJSONObject("geometry_share_percent").getDouble("dedicated_pedestrian")
                require(distance.isFinite() && distance > 0 && share.isFinite() && share in 0.0..100.0)
                PilotRoute(id, title, distance, share, points)
            }
            val destination = result.getJSONObject("destination")
            val latLon = destination.getJSONArray("coordinates_lat_lon")
            val gap = destination.getDouble("snap_gap_m")
            require(gap.isFinite() && gap >= 0)
            PilotData(facilities, routes, pilotPoint(latLon.getDouble(0), latLon.getDouble(1)), gap, false, null)
        } catch (e: JSONException) {
            throw IllegalArgumentException("파일럿 자료 형식 오류: ${e.message}", e)
        }

        private fun facilityAddress(properties: JSONObject): String? =
            listOf("소재지도로명주소", "소재지지번주소").asSequence()
                .map { properties.optString(it).trim() }.firstOrNull { it.isNotEmpty() && it != "null" }

        private fun facilityDetail(properties: JSONObject, kind: String, point: GeoPoint?): String {
            fun value(vararg keys: String) = keys.asSequence().map { properties.optString(it).trim() }
                .firstOrNull { it.isNotEmpty() && it != "null" }
            val lines = mutableListOf("주소: ${facilityAddress(properties) ?: "정보 없음"}")
            if (kind == "police_osm_candidate") {
                value("name")?.let { lines.add("시설명: $it") }
                lines.add("OSM 경찰시설 후보 · 공식 여부/출입구 미확인")
            }
            for ((label, key) in listOf("관리기관" to "관리기관명", "설치연도" to "설치연도", "용도" to "설치목적구분", "설치장소" to "설치장소유형")) {
                value(key)?.let { lines.add("$label: $it") }
            }
            if (kind == "bell") lines.add("경찰 연계: " + when (value("경찰연계유무")) {
                "Y" -> "연계됨 (원천 기준)"
                "N" -> "연계 없음 (원천 기준)"
                else -> "정보 없음"
            })
            point?.let { lines.add(String.format(java.util.Locale.KOREA, "지도 좌표: %.6f, %.6f", it.latitude, it.longitude)) }
            if (kind == "lamp") lines.add("좌표 공유 기록: ${properties.optInt("same_coordinate_records", 1)}건 (원본 기록 기준)")
            lines.add("기준일: ${value("data_as_of") ?: "미기록"}")
            lines.add("출처: " + when (kind) {
                "lamp" -> "경기데이터드림 · 시흥시"
                "police_osm_candidate" -> "OpenStreetMap 기여자 / ODbL"
                else -> "시흥시 공공데이터"
            })
            value("source_url")?.let { lines.add("원문: $it") }
            return lines.joinToString("\n\n")
        }

        private fun JSONArray.objects() = (0 until length()).map { getJSONObject(it) }
        private fun JSONArray.points() = (0 until length()).map { getJSONArray(it).point() }
        private fun JSONArray.point(): GeoPoint {
            require(length() == 2) { "좌표는 [경도, 위도]여야 합니다" }
            return pilotPoint(getDouble(1), getDouble(0))
        }
        private fun pilotPoint(latitude: Double, longitude: Double): GeoPoint {
            require(latitude.isFinite() && longitude.isFinite() && latitude in 37.334..37.359 && longitude in 126.719..126.751) {
                "파일럿 범위 밖 좌표 또는 경위도 순서 오류"
            }
            return GeoPoint(latitude, longitude)
        }
    }
}
