package kr.ac.tukorea.nightsafety

import org.junit.Assert.*
import org.junit.Test

class ServerBundleParserTest {
    @Test fun keepsRouteCountsDistinctFromMapFiltersAndUnknownFromZero() {
        val json = org.json.JSONObject(officialResponse())
        json.getJSONObject("data").getJSONArray("routes").getJSONObject(0)
            .put("facility_counts", org.json.JSONObject("""{"cctv":0,"emergency_bell":16,"security_lamp":12}"""))
        val data = ServerBundleParser.parse(json.toString(), emptyList())
        assertEquals(mapOf("cctv" to 0, "emergency_bell" to 16, "security_lamp" to 12), data.routes.single().facilityCounts)
        assertTrue(data.visibleFacilities(emptySet()).isEmpty())
        assertEquals(12, data.routes.single().facilityCounts["security_lamp"])
        val partial = org.json.JSONObject(response)
        partial.getJSONObject("data").put("missing_types", org.json.JSONArray(listOf("security_lamp")))
        partial.getJSONObject("data").getJSONArray("routes").getJSONObject(0)
            .put("facility_counts", org.json.JSONObject("""{"cctv":0,"emergency_bell":16,"security_lamp":null}"""))
        val parsed = ServerBundleParser.parse(partial.toString(), emptyList())
        assertEquals(0, parsed.routes.single().facilityCounts["cctv"])
        assertNull(parsed.routes.single().facilityCounts["security_lamp"])
        assertEquals(listOf("security_lamp"), parsed.missingTypes)
        assertTrue(ServerBundleParser.parse(response, emptyList()).routes.single().facilityCounts.values.all { it == null })
    }

    @Test fun rejectsNegativeFractionalOrNonfiniteRouteCounts() {
        for (bad in listOf(-1, .5, Double.MAX_VALUE)) {
            val json = org.json.JSONObject(officialResponse())
            json.getJSONObject("data").getJSONArray("routes").getJSONObject(0)
                .put("facility_counts", org.json.JSONObject().put("cctv", bad))
            assertThrows(IllegalArgumentException::class.java) { ServerBundleParser.parse(json.toString(), emptyList()) }
        }
    }

    private fun officialResponse(): String {
        val json = org.json.JSONObject(response)
        val data = json.getJSONObject("data")
        data.put("missing_types", org.json.JSONArray())
        data.put("score_basis_types", org.json.JSONArray(listOf("cctv", "emergency_bell", "security_lamp")))
        data.getJSONArray("routes").getJSONObject(0).apply {
            put("score_status", "complete"); put("safety_score", 35)
            put("average_safety", 40); put("weak_safety", 23.33333333333333)
        }
        return json.toString()
    }

    @Test fun parsesThreeTypeOfficialScoreWithoutPromotingAnIncompleteRoute() {
        val data = ServerBundleParser.parse(officialResponse(), emptyList())
        assertEquals(35.0, data.safetyScore!!, .001)
        assertEquals("complete", data.routes.single().scoreStatus)
        assertFalse(data.complete)
        assertFalse(data.sourceSummary.contains("과거 CCTV"))
    }

    @Test fun rejectsInconsistentOfficialMetricsAndMissingLightingBasis() {
        for (raw in listOf(officialResponse().replace("\"average_safety\":40", "\"average_safety\":10"),
            officialResponse().replace("\"security_lamp\"", "\"smart_lamp\""))) {
            assertThrows(IllegalArgumentException::class.java) { ServerBundleParser.parse(raw, emptyList()) }
        }
    }

    @Test fun finalServerRolesDetermineSafetyPreferenceInsteadOfGenerationProfile() {
        val json = org.json.JSONObject(officialResponse())
        val routes = json.getJSONObject("data").getJSONArray("routes")
        routes.getJSONObject(0).put("generated_profiles", org.json.JSONArray(listOf("safe")))
        val winner = org.json.JSONObject(routes.getJSONObject(0).toString()).apply {
            put("route_id", "winner"); put("roles", org.json.JSONArray(listOf("safe")))
            put("generated_profiles", org.json.JSONArray(listOf("balanced")))
            put("safety_score", 40); put("average_safety", 40); put("weak_safety", 40)
        }
        routes.put(winner)
        val parsed = ServerBundleParser.parse(json.toString(), emptyList())
        assertEquals("winner", parsed.routes.single { "safe" in it.profiles }.id)
    }

    private val response = """{
      "schema_version":"1.0","request_id":"unit","status":"partial_success",
      "data":{"versions":{"graph_version":"g1","facility_version":"f1"},
        "score_basis_types":["cctv","emergency_bell"],"missing_types":["smart_lamp"],
        "source_states":[],"selected_roles":{"fast":"r1","safe":null},
        "routes":[{"route_id":"r1","roles":["fast"],"route_status":"incomplete",
          "physical_verification":"unverified","distance_m":100,"duration_s":83.33,
          "pedestrian_percent":10,"safety_score":null,"available_data_score":42,
          "score_status":"partial","edge_references":["10:1:2"],"segments":[],
          "origin_anchor":{"gap_m":0,"requested":{"latitude":37.34,"longitude":126.73}},
          "destination_anchor":{"gap_m":12,"requested":{"latitude":37.35,"longitude":126.74}},
          "geometry":{"type":"LineString","coordinates":[[126.73,37.34],[126.74,37.35]]}}]}}
    """.trimIndent()

    @Test fun parsesPartialScoresWithoutClaimingAnOfficialScore() {
        val data = ServerBundleParser.parse(response, emptyList())
        assertEquals(1, data.routes.size)
        assertEquals(42.0, data.routes.first().availableDataScore!!, .001)
        assertNull(data.safetyScore)
        assertFalse(data.complete)
        assertEquals("g1", data.versions["graph_version"])
        assertEquals(126.73, data.routes.first().points.first().longitude, .00001)
        assertEquals(response, data.snapshotJson)
    }

    @Test fun rejectsForgedOfficialScoreOrCoordinateOrErrorEnvelope() {
        for (bad in listOf(response.replace("\"safety_score\":null", "\"safety_score\":90"),
            response.replace("126.73,37.34", "999,37.34"),
            """{"schema_version":"1.0","status":"error","error":{"message":"범위 밖"}}""")) {
            assertThrows(IllegalArgumentException::class.java) { ServerBundleParser.parse(bad, emptyList()) }
        }
    }

    @Test fun timeoutWithoutCandidatesIsNotReportedAsNoRoute() {
        val incomplete = org.json.JSONObject(response)
        incomplete.getJSONObject("data").put("routes", org.json.JSONArray()).put("candidate_search_complete", false)
        assertThrows(IllegalArgumentException::class.java) { ServerBundleParser.parse(incomplete.toString(), emptyList()) }
        incomplete.put("status", "no_route")
        assertTrue(ServerBundleParser.parse(incomplete.toString(), emptyList()).routes.isEmpty())
    }

    @Test fun alreadyAtDestinationHasNoDrawableLineOrScore() {
        val zero = org.json.JSONObject(response).put("status", "already_at_destination")
        zero.getJSONObject("data").getJSONArray("routes").getJSONObject(0).apply {
            put("route_status", "already_at_destination"); put("geometry", org.json.JSONObject.NULL)
            put("distance_m", 0); put("duration_s", 0); put("available_data_score", org.json.JSONObject.NULL)
        }
        val route = ServerBundleParser.parse(zero.toString(), emptyList()).routes.single()
        assertTrue(route.points.isEmpty())
        assertEquals(0.0, route.distanceMeters, .0001)
        assertEquals(0.0, route.estimatedMinutes, .0001)
        assertNull(route.availableDataScore)
    }
}
