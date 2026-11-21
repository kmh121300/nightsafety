package kr.ac.tukorea.nightsafety

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

object ServerBundleParser {
    fun parse(json: String, facilities: List<Facility>): PilotData = try {
        val envelope = JSONObject(json)
        require(envelope.getString("schema_version") == "1.0") { "서버 응답 버전이 맞지 않습니다" }
        require(envelope.getString("status") in listOf("success", "partial_success", "no_route", "already_at_destination")) {
            envelope.optJSONObject("error")?.optString("message") ?: "경로 조회 실패"
        }
        val data = envelope.getJSONObject("data")
        if (envelope.getString("status") == "partial_success" && data.getJSONArray("routes").length() == 0 && !data.optBoolean("candidate_search_complete", true)) {
            throw IllegalArgumentException("경로 계산 시간이 초과됐습니다 · 다시 검색하세요")
        }
        val missing = data.getJSONArray("missing_types").strings()
        val basis = data.getJSONArray("score_basis_types").strings()
        val versions = data.getJSONObject("versions").let { obj -> obj.keys().asSequence().associateWith { obj.getString(it) } }
        val routes = data.getJSONArray("routes").objects().map { route ->
            val status = route.getString("route_status")
            require(status in setOf("complete", "incomplete", "already_at_destination"))
            val official = route.numberOrNull("safety_score")
            val average = route.numberOrNull("average_safety")
            val weak = route.numberOrNull("weak_safety")
            require(missing.isEmpty() || official == null) { "누락 자료가 있는 공식 점수는 사용할 수 없습니다" }
            val geometry = route.optJSONObject("geometry")
            val points = if (geometry == null) emptyList() else {
                require(geometry.getString("type") == "LineString")
                geometry.getJSONArray("coordinates").points().also { require(it.size >= 2) }
            }
            val distance = route.number("distance_m", 0.0, 10000.0)
            require(distance == 0.0 || points.size >= 2)
            if (official != null) {
                require(distance > 0 && route.getString("score_status") == "complete" &&
                    basis.toSet() == setOf("cctv", "emergency_bell", "security_lamp") &&
                    average != null && weak != null && average >= weak && official in weak..average &&
                    kotlin.math.abs(official - (.7 * average + .3 * weak)) < .000001) { "시설 지표의 계산 기준이 맞지 않습니다" }
            } else {
                require(average == null && weak == null && route.getString("score_status") != "complete") { "시설 지표가 누락됐습니다" }
            }
            val profiles = (route.optJSONArray("roles") ?: route.optJSONArray("generated_profiles") ?: JSONArray()).strings()
            val rawCounts = route.optJSONObject("facility_counts")
            val counts = listOf("cctv", "emergency_bell", "security_lamp").associateWith { kind ->
                if (rawCounts == null || rawCounts.isNull(kind)) null else {
                    val count = rawCounts.number(kind, 0.0, Int.MAX_VALUE.toDouble())
                    require(count % 1.0 == 0.0 && kind !in missing) { "시설 개수의 자료 상태가 맞지 않습니다" }
                    count.toInt()
                }
            }
            val title = profiles.mapNotNull {
                when (it) {
                    "fast" -> "빠른 경로"
                    "safe" -> if (official != null) "안전 우선 경로" else "부분 시설지표 후보"
                    "balanced" -> "균형 경로"
                    "pedestrian" -> "보행선 우선"
                    else -> null
                }
            }.distinct().joinToString(" · ").ifEmpty { "비교 후보" }
            val segments = (route.optJSONArray("segments") ?: JSONArray()).objects().map { segment ->
                RouteSegment(segment.number("length_m", 0.0, 10000.0), (segment.numberOrNull("safety_score") ?: segment.numberOrNull("available_data_score")),
                    segment.optString("grade", "unknown"), segment.getJSONObject("geometry").getJSONArray("coordinates").points())
            }
            PilotRoute(route.getString("route_id"), title, distance,
                route.numberOrNull("pedestrian_percent") ?: 0.0, points,
                route.number("duration_s", 0.0, 86400.0), status,
                route.numberOrNull("available_data_score"), route.getString("score_status"), basis, segments,
                (route.optJSONArray("edge_references") ?: JSONArray()).strings(), profiles,
                (route.optJSONArray("weak_member_ranges") ?: JSONArray()).objects().map { range ->
                    RouteSegment(range.getDouble("end_m") - range.getDouble("start_m"), (range.numberOrNull("safety_score") ?: range.numberOrNull("available_data_score")),
                        "unknown", range.getJSONObject("geometry").getJSONArray("coordinates").points())
                }, official, average, weak, counts)
        }
        val first = data.getJSONArray("routes").optJSONObject(0)
        fun endpoint(name: String, fallback: GeoPoint): GeoPoint {
            val point = first?.optJSONObject(name)?.optJSONObject("requested") ?: return fallback
            return checkedPoint(point.getDouble("latitude"), point.getDouble("longitude"))
        }
        val origin = endpoint("origin_anchor", GeoPoint(37.3418341, 126.7315593))
        val destination = endpoint("destination_anchor", GeoPoint(37.3517100, 126.7427421))
        val gap = first?.optJSONObject("destination_anchor")?.optDouble("gap_m", 0.0) ?: 0.0
        require(gap.isFinite() && gap >= 0)
        PilotData(facilities, routes, destination, gap,
            routes.isNotEmpty() && routes.all { it.routeStatus == "complete" }, routes.firstOrNull()?.safetyScore, origin, json, versions,
            if (basis.contains("security_lamp")) "CCTV·비상벨·보안등 · 공공 CSV 기준" else "이전 버전의 부분 시설지표",
            missingTypes = missing)
    } catch (error: JSONException) {
        throw IllegalArgumentException("서버 응답 형식 오류", error)
    }

    fun checkedPoint(latitude: Double, longitude: Double): GeoPoint {
        require(latitude.isFinite() && longitude.isFinite() && latitude in 37.334..37.359 && longitude in 126.719..126.751) {
            "현재는 한국공학대학교–정왕역 파일럿 범위만 지원합니다"
        }
        return GeoPoint(latitude, longitude)
    }

    private fun JSONObject.number(name: String, min: Double, max: Double): Double = getDouble(name).also {
        require(it.isFinite() && it in min..max) { "잘못된 $name 값입니다" }
    }
    private fun JSONObject.numberOrNull(name: String): Double? =
        if (!has(name) || isNull(name)) null else number(name, 0.0, 100.0)
    private fun JSONArray.strings() = (0 until length()).map { getString(it) }
    private fun JSONArray.objects() = (0 until length()).map { getJSONObject(it) }
    private fun JSONArray.points() = (0 until length()).map {
        getJSONArray(it).let { pair -> require(pair.length() == 2); checkedPoint(pair.getDouble(1), pair.getDouble(0)) }
    }
}
