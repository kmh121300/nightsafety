package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test

class FacilityOverlayQueueTest {
    private val facilities = (1..20).map {
        Facility("lamp:$it", "lamp", listOf(GeoPoint(37.35, 126.73)), false, null, "보안등", "")
    }

    @Test fun largeUpdatesYieldBetweenBatchesAndUnchangedUpdatesDoNothing() {
        val frames = ArrayDeque<() -> Unit>()
        val added = mutableListOf<Facility>()
        val queue = FacilityOverlayQueue({ frames.add(it) }, { fail("Unexpected remove") }, { added.add(it) })
        queue.update(facilities)
        assertTrue(added.isEmpty())
        frames.removeFirst().invoke()
        assertEquals(8, added.size)
        while (frames.isNotEmpty()) frames.removeFirst().invoke()
        assertEquals(facilities, added)
        queue.update(facilities)
        assertTrue(frames.isEmpty())
    }

    @Test fun rapidFilterChangeReconcilesOnlyActuallyRenderedFacilities() {
        val frames = ArrayDeque<() -> Unit>()
        val shown = mutableSetOf<String>()
        val queue = FacilityOverlayQueue({ frames.add(it) }, { shown.remove(it.id) }, { shown.add(it.id) })
        queue.update(facilities)
        frames.removeFirst().invoke()
        assertEquals(8, shown.size)
        queue.update(emptyList())
        while (frames.isNotEmpty()) frames.removeFirst().invoke()
        assertTrue(shown.isEmpty())
        queue.update(facilities)
        while (frames.isNotEmpty()) frames.removeFirst().invoke()
        assertEquals(facilities.map { it.id }.toSet(), shown)
    }

    @Test fun destroyedMapDoesNotRunPendingSdkCalls() {
        val frames = ArrayDeque<() -> Unit>()
        val queue = FacilityOverlayQueue({ frames.add(it) }, { fail("After close") }, { fail("After close") })
        queue.update(facilities)
        queue.cancel()
        while (frames.isNotEmpty()) frames.removeFirst().invoke()
    }
}
