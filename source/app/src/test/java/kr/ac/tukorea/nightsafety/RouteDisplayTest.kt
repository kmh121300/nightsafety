package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test
import kotlin.math.cos

class RouteDisplayTest {
    private fun point(x: Double, y: Double) = GeoPoint(37.3465 + y / 111_195.0,
        126.735 + x / (111_195.0 * cos(Math.toRadians(37.3465))))
    private fun facility(id: String, x: Double, y: Double, kind: String = "cctv") =
        Facility(id, kind, listOf(point(x, y)), false, null, id, "")
    private val line = listOf(point(0.0, 0.0), point(1000.0, 0.0))
    private fun data(facilities: List<Facility>) = PilotData(facilities,
        listOf(PilotRoute("a", "A", 1000.0, 0.0, line, safetyScore = 42.0),
            PilotRoute("b", "B", 1000.0, 0.0, line.map { it.copy(latitude = it.latitude + .01) })),
        point(1010.0, 0.0), 10.0, false, null, point(0.0, 0.0))

    @Test fun includesSegmentMiddleAndCapsDistanceAt100Meters() {
        val near = facility("near", 500.0, 99.0)
        val far = facility("far", 500.0, 101.0)
        val beyondEnd = facility("past", 1101.0, 0.0)
        assertEquals(listOf(near), facilitiesNearRoute(listOf(near, far, beyondEnd), line))
        assertTrue(facilitiesNearRoute(listOf(near), emptyList()).isEmpty())
        assertEquals(listOf(near), facilitiesNearRoute(listOf(near), listOf(point(500.0, 0.0))))
    }

    @Test fun includesCrossingAndContainingPolygonsEvenWithDistantVertices() {
        fun polygon(id: String, left: Double, right: Double) = Facility(id, "police_osm_candidate",
            listOf(point(left, -300.0), point(right, -300.0), point(right, 300.0), point(left, 300.0)),
            true, null, id, "")
        val cross = polygon("cross", 400.0, 600.0)
        val contains = polygon("contains", -300.0, 1300.0)
        val far = polygon("far", 1500.0, 1800.0)
        assertEquals(listOf(cross, contains), facilitiesNearRoute(listOf(cross, contains, far), line))
    }

    @Test fun routeAndKindChangesRefreshDisplayWithoutChangingScoresOrSourceFacilities() {
        val near = facility("near", 500.0, 50.0)
        val lamp = facility("lamp", 600.0, 50.0, "lamp")
        val data = data(listOf(near, lamp))
        val first = data.mapFacilities(0, setOf("cctv", "lamp"))
        assertEquals(listOf(near, lamp), first)
        assertSame(first, data.mapFacilities(0, setOf("cctv", "lamp")))
        assertEquals(listOf(lamp), data.mapFacilities(0, setOf("lamp")))
        assertTrue(data.mapFacilities(1, setOf("cctv", "lamp")).isEmpty())
        assertEquals(first, data.mapFacilities(0, setOf("cctv", "lamp")))
        assertTrue(data.mapFacilities(-1, setOf("cctv")).isEmpty())
        assertEquals(listOf(near, lamp), data.facilities)
        assertEquals(42.0, data.routes.first().safetyScore!!, 0.0)
        assertEquals(line, data.routes.first().points)
    }

    @Test fun pinsKeepRequestedEndpointAndNeverExtendIncompleteGeometry() {
        val data = data(emptyList())
        val pointsBefore = data.routes.first().points.toList()
        assertEquals(listOf("출발" to data.origin!!, "도착" to data.destination), data.routeEndpoints(0))
        assertNotEquals(data.destination, pointsBefore.last())
        assertEquals(pointsBefore, data.routes.first().points)
        assertTrue(data.copy(routes = emptyList()).routeEndpoints(0).isEmpty())
        val zero = data.copy(origin = data.destination,
            routes = listOf(data.routes.first().copy(points = emptyList(), routeStatus = "already_at_destination")))
        assertEquals(listOf("출발·도착" to data.destination), zero.routeEndpoints(0))
    }
}
