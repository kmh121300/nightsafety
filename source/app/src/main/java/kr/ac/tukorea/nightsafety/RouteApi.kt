package kr.ac.tukorea.nightsafety

import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URI
import java.net.URLEncoder

/** Development URLs use adb reverse. No app keys or request coordinates are logged. */
class RouteApi(private val baseUrl: String = BuildConfig.API_BASE_URL) {
    @Volatile private var active: HttpURLConnection? = null

    init {
        val uri = URI(baseUrl)
        require(uri.userInfo == null && uri.query == null && uri.fragment == null)
        require(uri.scheme == "https" || (BuildConfig.DEBUG && uri.scheme == "http" && uri.host in setOf("127.0.0.1", "localhost", "10.0.2.2"))) {
            "서버 주소는 HTTPS 또는 개발용 localhost여야 합니다"
        }
    }

    fun compare(origin: NamedPlace, destination: NamedPlace): String = request("/v1/routes/compare", JSONObject()
        .put("region_id", "siheung").put("origin", origin.json()).put("destination", destination.json())
        .put("max_extra_time_s", 600))

    fun evaluate(route: PilotRoute): String = request("/v1/routes/evaluate", JSONObject()
        .put("route_id", route.id).put("edge_references", org.json.JSONArray(route.edgeReferences)))

    fun places(query: String): List<NamedPlace> {
        require(query.trim().length in 1..100) { "검색어는 1~100자로 입력하세요" }
        val data = JSONObject(request("/v1/places?q=" + URLEncoder.encode(query.trim(), "UTF-8"))).getJSONObject("data").getJSONArray("places")
        return (0 until data.length()).map { index ->
            val place = data.getJSONObject(index)
            NamedPlace(ServerBundleParser.checkedPoint(place.getDouble("latitude"), place.getDouble("longitude")), place.getString("label"), "osm")
        }
    }

    fun cancel() { active?.disconnect(); active = null }

    fun snap(point: GeoPoint): SnappedPlace = parseSnappedPlace(request("/v1/places/snap", JSONObject()
        .put("latitude", point.latitude).put("longitude", point.longitude)))

    private fun request(path: String, body: JSONObject? = null): String {
        val connection = URI(baseUrl.trimEnd('/') + path).toURL().openConnection() as HttpURLConnection
        active = connection
        try {
            connection.connectTimeout = 5000
            connection.readTimeout = 20000
            connection.instanceFollowRedirects = false
            connection.setRequestProperty("Accept", "application/json")
            if (body != null) {
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                connection.outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
            }
            val stream = if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream
            val output = ByteArrayOutputStream()
            stream?.use { input ->
                val buffer = ByteArray(8192)
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    require(output.size() + count <= 4_000_000) { "서버 응답이 너무 큽니다" }
                    output.write(buffer, 0, count)
                }
            }
            val json = output.toString("UTF-8")
            if (connection.responseCode !in 200..299) {
                val message = runCatching { JSONObject(json).getJSONObject("error").getString("message") }.getOrDefault("서버 오류 ${connection.responseCode}")
                throw IllegalArgumentException(message)
            }
            return json
        } finally {
            if (active === connection) active = null
            connection.disconnect()
        }
    }
}

data class NamedPlace(val point: GeoPoint, val label: String, val source: String = "user_coordinate") {
    fun json(): JSONObject = JSONObject().put("latitude", point.latitude).put("longitude", point.longitude).put("label", label).put("source", source)
}

data class SnappedPlace(val point: GeoPoint, val gapMeters: Double)

internal fun parseSnappedPlace(response: String): SnappedPlace {
    val root = JSONObject(response)
    require(root.getString("status") == "success") { "보행 지점을 찾지 못했습니다" }
    val data = root.getJSONObject("data")
    val place = data.getJSONObject("place")
    val point = ServerBundleParser.checkedPoint(place.getDouble("latitude"), place.getDouble("longitude"))
    val gap = data.getDouble("gap_m")
    require(gap.isFinite() && gap >= 0) { "보정 거리가 올바르지 않습니다" }
    return SnappedPlace(point, gap)
}
