package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test
import org.json.JSONObject

class PilotDataTest {
    private fun asset(name: String) = javaClass.classLoader!!.getResource(name)!!.readText()
    private fun data() = PilotData.parse(asset("pilot-facilities.geojson"), asset("result-v2.json"), asset("routes-v2.geojson"), asset("pilot-security-lights.geojson"))

    @Test fun loadsRealFacilitiesAndSecurityLightsWithoutInventingSmartLamps() {
        val data = data()
        assertEquals(270, data.facilities.count { it.kind == "cctv" })
        assertEquals(238, data.facilities.count { it.kind == "bell" })
        assertEquals(870, data.facilities.count { it.kind == "lamp" })
        assertEquals(0, data.facilities.count { it.kind == "smart_lamp" })
        val lamp = data.facilities.first { it.kind == "lamp" }
        assertEquals("2026-02-24", lamp.dataAsOf)
        assertTrue(lamp.title.startsWith("보안등"))
        assertTrue(lamp.detail.contains("좌표 공유 기록"))
        assertFalse(lamp.detail.contains("점수 제외"))
        assertFalse(lamp.detail.contains("작동"))
        assertEquals(1381, data.facilities.map { it.id }.distinct().size)
        assertEquals(2, data.facilities.count { it.kind == "police_osm_candidate" && !it.polygon })
        assertEquals(1, data.facilities.count { it.polygon })
        assertEquals("2026-01-20", data.facilities.first().dataAsOf)
    }

    @Test fun preservesLongitudeLatitudeOrderAndUnverifiedEndpoints() {
        val data = data()
        assertEquals(126.725893, data.facilities.first().points.first().longitude, 1e-8)
        assertEquals(37.35589946, data.facilities.first().points.first().latitude, 1e-8)
        assertFalse(data.complete)
        assertNull(data.safetyScore)
        assertEquals(12.56, data.exitGapMeters, 0.01)
        assertEquals(1572.40, data.routes.first().distanceMeters, 0.01)
        assertEquals(1932.56, data.routes.last().distanceMeters, 0.01)
        assertTrue(data.routes.all { it.points.size > 2 })
    }

    @Test fun facilityDetailsShowHumanReadableSourcesWithoutInternalKeys() {
        val facilities = data().facilities
        val lamp = facilities.first { it.kind == "lamp" }
        assertTrue(lamp.detail.contains("기준일: 2026-02-24"))
        assertTrue(lamp.detail.contains("출처: 경기데이터드림"))
        assertTrue(lamp.detail.contains("주소:"))
        assertTrue(facilities.first { it.kind == "bell" }.detail.contains("경찰 연계:"))
        assertTrue(facilities.first { it.kind == "police_osm_candidate" }.detail.contains("OpenStreetMap"))
        for (facility in facilities) {
            for (internal in listOf("csv_row:", "facility_id:", "source_sha256:", "operational_status:", "kind:")) {
                assertFalse(facility.detail.contains(internal))
            }
        }
    }

    @Test fun policeCandidatesKeepTheirReadableQualification() {
        for (facility in data().facilities.filter { it.kind == "police_osm_candidate" }) {
            assertTrue(facility.detail.contains("OSM 경찰시설 후보"))
            assertTrue(facility.detail.contains("공식 여부/출입구 미확인"))
        }
    }

    @Test fun rejectsMalformedOrOutOfPilotCoordinates() {
        val validFacilities = asset("pilot-facilities.geojson")
        for (invalid in listOf("{}", validFacilities.replace("126.725893", "999.0"), validFacilities.replace("126.725893", "37.0"))) {
            assertThrows(IllegalArgumentException::class.java) {
                PilotData.parse(invalid, asset("result-v2.json"), asset("routes-v2.geojson"))
            }
        }
    }

    @Test fun filtersFacilitiesWithoutChangingTheUnderlyingData() {
        val data = data()
        assertTrue(data.visibleFacilities(emptySet()).isEmpty())
        assertEquals(1381, data.facilities.size)
        assertEquals(870, data.visibleFacilities(setOf("lamp")).size)
        assertEquals(511, data.visibleFacilities(setOf("cctv", "bell", "police_osm_candidate")).size)
        assertTrue(data.visibleFacilities(setOf("bell")).all { it.kind == "bell" })
    }

    @Test fun rejectsDisconnectedRouteGeometryRatherThanAddingAConnector() {
        val geometry = JSONObject(asset("routes-v2.geojson"))
        val features = geometry.getJSONArray("features")
        val secondEdge = features.getJSONObject(1).getJSONObject("geometry").getJSONArray("coordinates")
        secondEdge.getJSONArray(0).put(0, secondEdge.getJSONArray(0).getDouble(0) + 0.0001)
        assertThrows(IllegalArgumentException::class.java) {
            PilotData.parse(asset("pilot-facilities.geojson"), asset("result-v2.json"), geometry.toString())
        }
    }
    @Test fun titlesUseRoadThenParcelAddressAndHideRawRecordNames() {
        val json = JSONObject(asset("pilot-facilities.geojson"))
        val props = json.getJSONArray("features").getJSONObject(0).getJSONObject("properties")
        fun first() = PilotData.parse(json.toString(), asset("result-v2.json"), asset("routes-v2.geojson")).facilities.first()
        props.put("name", "CCTV · 22").put("소재지도로명주소", "  도로명 테스트  ").put("소재지지번주소", "지번 테스트")
        assertEquals("CCTV · 도로명 테스트", first().title)
        props.put("소재지도로명주소", "null")
        assertEquals("CCTV · 지번 테스트", first().title)
        props.put("소재지지번주소", " ")
        assertEquals("CCTV · 주소 정보 없음", first().title)
        assertEquals("cctv:22", first().id)
    }

    @Test fun bundledCctvAndBellTitlesContainVerifiedSourceAddresses() {
        val facilities = data().facilities
        val firstCctv = facilities.first { it.kind == "cctv" }
        assertEquals("CCTV · 경기도 시흥시 정왕대로53번길 14", firstCctv.title)
        val firstBell = facilities.first { it.kind == "bell" }
        assertEquals("비상벨 · 경기도 시흥시 정왕동 1208-8", firstBell.title)
        assertTrue(firstBell.detail.contains("경기도 시흥시 정왕동 1208-8"))
        for (facility in facilities.filter { it.kind in setOf("cctv", "bell", "lamp") }) {
            assertFalse(facility.title.matches(Regex(".* · [0-9]+")))
        }
    }

}
