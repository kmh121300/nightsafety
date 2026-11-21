package kr.ac.tukorea.nightsafety

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class SnappedPlaceTest {
    private fun response(latitude: Double = 37.349, gap: Double = 111.2): String = JSONObject()
        .put("status", "success").put("data", JSONObject().put("gap_m", gap)
            .put("place", JSONObject().put("latitude", latitude).put("longitude", 126.74))).toString()

    @Test fun readsAdjustedCoordinateAndGap() {
        val snap = parseSnappedPlace(response())
        assertEquals(GeoPoint(37.349, 126.74), snap.point)
        assertEquals(111.2, snap.gapMeters, 0.001)
        assertEquals(0.0, parseSnappedPlace(response(gap = 0.0)).gapMeters, 0.0)
    }

    @Test fun rejectsNegativeGapAndOutsidePilot() {
        assertThrows(IllegalArgumentException::class.java) { parseSnappedPlace(response(gap = -1.0)) }
        assertThrows(IllegalArgumentException::class.java) { parseSnappedPlace(response(latitude = 38.0)) }
        assertThrows(IllegalArgumentException::class.java) {
            val json = JSONObject(response())
            json.getJSONObject("data").put("gap_m", "NaN")
            parseSnappedPlace(json.toString())
        }
        assertThrows(IllegalArgumentException::class.java) {
            parseSnappedPlace(JSONObject(response()).put("status", "error").toString())
        }
    }
}
