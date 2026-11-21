package kr.ac.tukorea.nightsafety

import kotlin.math.abs

private val KIND_ORDER = listOf("cctv", "bell", "lamp", "police_osm_candidate")

internal fun facilityKindLabel(kind: String): String = when (kind) {
    "cctv" -> "CCTV"
    "bell" -> "비상벨"
    "lamp" -> "보안등"
    "police_osm_candidate" -> "경찰시설 후보"
    else -> kind
}

internal data class FacilityKindGroup(
    val kind: String,
    val label: String,
    val count: Int,
    val members: List<Facility>
) {
    val summaryText: String get() = "$label ${count}개"
}

internal fun summarizeFacilityCluster(members: List<Facility>): List<FacilityKindGroup> {
    if (members.isEmpty()) return emptyList()
    val grouped = members.groupBy { it.kind }
    val orderedKinds = KIND_ORDER.filter { it in grouped } + (grouped.keys - KIND_ORDER.toSet()).sorted()
    return orderedKinds.map { kind ->
        val list = grouped.getValue(kind)
        FacilityKindGroup(kind, facilityKindLabel(kind), list.size, list)
    }
}

internal fun clusterSummaryTitle(members: List<Facility>): String =
    summarizeFacilityCluster(members).joinToString(" · ") { it.summaryText }

internal data class FacilityCluster(val members: List<Facility>, val x: Double, val y: Double) {
    val widthDp: Double get() = if (members.size == 1) 28.0 else 48.0
    val heightDp: Double get() = if (members.size == 1) 28.0 else 36.0
    val overlay: Facility get() = if (members.size == 1) members.first() else members.first().copy(
        id = "facility-cluster:" + members.joinToString("") { "${it.id.length}:${it.id}" },
        title = clusterSummaryTitle(members), detail = "")
}

/** Merge displayed badge bounds, keeping a real member as the stable representative. */
internal fun clusterFacilities(
    facilities: List<Facility>, density: Double, project: (GeoPoint) -> Pair<Double, Double>
): List<FacilityCluster> {
    require(density.isFinite() && density > 0)
    val groups = facilities.filter { !it.polygon }.sortedBy { it.id }.map { facility ->
        val (x, y) = project(facility.points.first())
        FacilityCluster(listOf(facility), x, y)
    }.toMutableList()
    var changed = true
    while (changed) {
        changed = false
        merge@ for (i in groups.indices) for (j in i + 1 until groups.size) {
            val a = groups[i]; val b = groups[j]
            if (abs(a.x - b.x) < (a.widthDp + b.widthDp) * density / 2 &&
                abs(a.y - b.y) < (a.heightDp + b.heightDp) * density / 2) {
                groups[i] = a.copy(members = (a.members + b.members).sortedBy { it.id })
                groups.removeAt(j)
                changed = true
                break@merge
            }
        }
    }
    return groups
}


/** Metadata can change even when SDK overlay geometry and membership stay identical. */
internal fun refreshShownClusters(
    shown: MutableMap<String, FacilityCluster>, desired: Map<String, FacilityCluster>
) {
    shown.keys.forEach { id -> desired[id]?.let { shown[id] = it } }
}
