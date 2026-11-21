package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test

class FacilityClusterTest {
    private fun facility(id: String, x: Double, y: Double = 0.0, kind: String = "cctv") =
        Facility(id, kind, listOf(GeoPoint(y, x)), false, null, id, "detail")
    private fun group(items: List<Facility>, scale: Double = 1.0) = clusterFacilities(items, 1.0) {
        it.longitude * scale to it.latitude * scale
    }

    @Test fun groupsOverlappingKindsAndKeepsEveryMemberExactlyOnce() {
        val a = facility("a", 0.0)
        val b = facility("b", 20.0, kind = "bell")
        val far = facility("far", 100.0)
        val result = group(listOf(far, b, a))
        assertEquals(listOf(2, 1), result.map { it.members.size })
        assertEquals(listOf(a, b), result.first().members)
        assertEquals(setOf(a, b, far), result.flatMap { it.members }.toSet())
        assertEquals(0.0, result.first().x, 0.0)
        assertEquals(48.0, result.first().widthDp, 0.0)
        assertEquals(36.0, result.first().heightDp, 0.0)
    }

    @Test fun enlargedCountBadgeCannotOverlapAnotherGroup() {
        // a/b merge grows the badge and then reaches c at36px.
        val result = group(listOf(facility("a", 0.0), facility("b", -10.0), facility("c", 36.0)))
        assertEquals(1, result.size)
        assertEquals(3, result.single().members.size)
    }

    @Test fun zoomFilterAndInputOrderRecomputeMembershipWithoutMutatingFacilities() {
        val input = listOf(facility("b", 20.0), facility("a", 0.0))
        assertEquals(group(input), group(input.reversed()))
        assertEquals(1, group(input).size)
        assertEquals(2, group(input, 3.0).size)
        assertEquals(1, group(input.take(1)).single().members.size)
        assertEquals(20.0, input.first().points.first().longitude, 0.0)
        assertEquals("detail", input.first().detail)
        assertTrue(group(emptyList()).isEmpty())
    }

    @Test fun densityBoundaryAndPolygonsDoNotLosePointMarkers() {
        val a = facility("a", 0.0)
        val b = facility("b", 28.0)
        assertEquals(2, group(listOf(a,b)).size)
        assertEquals(1, clusterFacilities(listOf(a,b), 2.0) { it.longitude to it.latitude }.size)
        assertTrue(group(listOf(a.copy(polygon = true))).isEmpty())
    }

    @Test fun refreshedMemberDetailsReachExistingNativeMarkersWithoutReinsertion() {
        val original = group(listOf(facility("a", 0.0), facility("b", 10.0))).single()
        val updated = original.copy(members = original.members.map { it.copy(title = "new title", detail = "new detail") })
        assertEquals(original.overlay, updated.overlay)
        val removed = group(listOf(facility("gone", 100.0))).single()
        val shown = mutableMapOf(original.overlay.id to original, removed.overlay.id to removed)
        refreshShownClusters(shown, mapOf(updated.overlay.id to updated))
        assertEquals("new detail", shown.getValue(updated.overlay.id).members.last().detail)
        assertSame(removed, shown.getValue(removed.overlay.id))
    }

    @Test fun summarizesOverlappingFacilitiesByKindCountInsteadOfAddresses() {
        val members = listOf(
            facility("bell-2", 0.0, kind = "bell"),
            facility("cctv-1", 0.0, kind = "cctv"),
            facility("bell-1", 0.0, kind = "bell"),
            facility("cctv-2", 0.0, kind = "cctv"),
            facility("lamp-1", 0.0, kind = "lamp")
        )
        val summary = summarizeFacilityCluster(members)
        assertEquals(listOf("CCTV 2개", "비상벨 2개", "보안등 1개"), summary.map { it.summaryText })
        assertEquals(listOf(2, 2, 1), summary.map { it.count })
        assertEquals("CCTV 2개 · 비상벨 2개 · 보안등 1개", clusterSummaryTitle(members))
        val cluster = FacilityCluster(members, 0.0, 0.0)
        assertEquals("CCTV 2개 · 비상벨 2개 · 보안등 1개", cluster.overlay.title)
    }
}
