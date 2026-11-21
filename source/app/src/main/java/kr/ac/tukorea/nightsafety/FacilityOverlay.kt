package kr.ac.tukorea.nightsafety

internal fun syncFacilityOverlays(
    previous: List<Facility>, current: List<Facility>,
    remove: (Facility) -> Unit, add: (Facility) -> Unit
) {
    val old = previous.associateBy { it.id }
    val next = current.associateBy { it.id }
    previous.filter { next[it.id] != it }.forEach(remove)
    current.filter { old[it.id] != it }.forEach(add)
}

internal class FacilityOverlayQueue(
    private val postFrame: (() -> Unit) -> Unit,
    private val remove: (Facility) -> Unit,
    private val add: (Facility) -> Unit
) {
    private val rendered = linkedMapOf<String, Facility>()
    private var revision = 0

    fun update(current: List<Facility>) {
        val version = ++revision
        val pending = ArrayDeque<() -> Unit>()
        syncFacilityOverlays(rendered.values.toList(), current,
            { facility -> pending.add { remove(facility); rendered.remove(facility.id) } },
            { facility -> pending.add { add(facility); rendered[facility.id] = facility } })
        fun step() {
            if (version != revision) return
            // SDK marker insertion blocks input when hundreds run in one main-thread turn.
            repeat(minOf(8, pending.size)) { pending.removeFirst().invoke() }
            if (pending.isNotEmpty()) postFrame(::step)
        }
        if (pending.isNotEmpty()) postFrame(::step)
    }

    fun cancel() { revision++ }
}
