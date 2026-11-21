package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test

class FacilityOverlayTest {
    private val cctv = Facility("cctv:1", "cctv", listOf(GeoPoint(37.35, 126.73)), false, null, "CCTV", "")
    private val lamp = cctv.copy(id = "lamp:1", kind = "lamp", title = "보안등")
    private val polygon = cctv.copy(id = "police:1", kind = "police_osm_candidate", polygon = true)

    @Test fun routeAndWeakOverlayRefreshesLeaveFacilitiesUntouched() {
        val facilities = listOf(cctv, lamp, polygon)
        val displayed = mutableListOf<Facility>()
        syncFacilityOverlays(emptyList(), facilities, { fail("Nothing to remove") }, { displayed.add(it) })
        assertEquals(facilities, displayed)
        syncFacilityOverlays(facilities, facilities.map { it.copy() },
            { fail("Unchanged facility removed") }, { fail("Unchanged facility recreated") })
    }

    @Test fun filtersRemoveAndRestoreOnlyTheirOwnFacilities() {
        val facilities = listOf(cctv, lamp, polygon)
        val removed = mutableListOf<Facility>()
        val added = mutableListOf<Facility>()
        val filtered = listOf(cctv, polygon)
        syncFacilityOverlays(facilities, filtered, { removed.add(it) }, { added.add(it) })
        assertEquals(listOf(lamp), removed)
        assertTrue(added.isEmpty())
        removed.clear()
        syncFacilityOverlays(filtered, facilities, { removed.add(it) }, { added.add(it) })
        assertTrue(removed.isEmpty())
        assertEquals(listOf(lamp), added)
    }

    @Test fun changedGeometryOrDetailsReplaceTheOldOverlayAndEmptyRemovesAll() {
        val changed = polygon.copy(points = listOf(GeoPoint(37.351, 126.731)), detail = "updated")
        val removed = mutableListOf<Facility>()
        val added = mutableListOf<Facility>()
        syncFacilityOverlays(listOf(cctv, polygon), listOf(cctv, changed), { removed.add(it) }, { added.add(it) })
        assertEquals(listOf(polygon), removed)
        assertEquals(listOf(changed), added)
        removed.clear()
        added.clear()
        syncFacilityOverlays(listOf(cctv, changed), emptyList(), { removed.add(it) }, { added.add(it) })
        assertEquals(listOf(cctv, changed), removed)
        assertTrue(added.isEmpty())
    }
}
