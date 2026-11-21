package kr.ac.tukorea.nightsafety

import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min

private data class XY(val x: Double, val y: Double)

/** Display-only 100m corridor; scoring and original geometry stay unchanged. */
internal fun facilitiesNearRoute(facilities: List<Facility>, route: List<GeoPoint>): List<Facility> {
    val origin = route.firstOrNull() ?: return emptyList()
    val longitudeScale = 111_195.0 * cos(Math.toRadians(origin.latitude))
    fun project(p: GeoPoint) = XY((p.longitude - origin.longitude) * longitudeScale,
        (p.latitude - origin.latitude) * 111_195.0)
    val line = route.map(::project)
    val edges = if (line.size == 1) listOf(line.first() to line.first()) else line.zipWithNext()
    return facilities.filter { facility ->
        val points = facility.points.map(::project)
        points.any { p -> edges.any { (a, b) -> distanceSquared(p, a, b) <= 10_000.0 } } ||
            (facility.polygon && points.isNotEmpty() &&
                (line.any { inside(it, points) } || points.indices.any { i ->
                    val a = points[i]; val b = points[(i + 1) % points.size]
                    edges.any { (c, d) -> intersects(a, b, c, d) ||
                        distanceSquared(c, a, b) <= 10_000.0 || distanceSquared(d, a, b) <= 10_000.0 }
                }))
    }
}

private fun distanceSquared(p: XY, a: XY, b: XY): Double {
    val dx = b.x - a.x; val dy = b.y - a.y
    val length = dx * dx + dy * dy
    val t = if (length == 0.0) 0.0 else (((p.x - a.x) * dx + (p.y - a.y) * dy) / length).coerceIn(0.0, 1.0)
    val x = p.x - a.x - t * dx; val y = p.y - a.y - t * dy
    return x * x + y * y
}

private fun intersects(a: XY, b: XY, c: XY, d: XY): Boolean {
    if (max(a.x, b.x) < min(c.x, d.x) || max(c.x, d.x) < min(a.x, b.x) ||
        max(a.y, b.y) < min(c.y, d.y) || max(c.y, d.y) < min(a.y, b.y)) return false
    fun cross(a: XY, b: XY, c: XY) = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    return cross(a, b, c) * cross(a, b, d) <= 0 && cross(c, d, a) * cross(c, d, b) <= 0
}

private fun inside(p: XY, ring: List<XY>): Boolean {
    var result = false
    var previous = ring.last()
    for (current in ring) {
        if ((current.y > p.y) != (previous.y > p.y) &&
            p.x < (previous.x - current.x) * (p.y - current.y) / (previous.y - current.y) + current.x) result = !result
        previous = current
    }
    return result
}

internal fun PilotData.routeEndpoints(selected: Int): List<Pair<String, GeoPoint>> {
    val route = routes.getOrNull(selected) ?: return emptyList()
    val start = origin ?: route.points.firstOrNull() ?: return if (route.routeStatus == "already_at_destination")
        listOf("출발·도착" to destination) else emptyList()
    return if (start == destination) listOf("출발·도착" to destination)
        else listOf("출발" to start, "도착" to destination)
}
