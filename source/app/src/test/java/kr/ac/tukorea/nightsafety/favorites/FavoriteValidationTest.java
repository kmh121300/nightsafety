package kr.ac.tukorea.nightsafety.favorites;

import org.junit.Test;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

public class FavoriteValidationTest {
    private FavoriteRoute valid() {
        FavoriteRoute route = new FavoriteRoute();
        route.title = "  집으로  ";
        route.originLatitude = 37.34;
        route.originLongitude = 126.73;
        route.destinationLatitude = 37.35;
        route.destinationLongitude = 126.74;
        route.destinationSource = "osm";
        route.snapshotJson = "{\"versions\":{\"graph_version\":\"g1\"},\"score_status\":\"incomplete\",\"safety_score\":null}";
        return route;
    }

    @Test public void acceptsIncompleteOwnSnapshotAndEndpointOnlyFavorite() {
        FavoriteRoute route = valid();
        FavoriteValidation.route(route);
        assertEquals("집으로", FavoriteValidation.title(route.title));
        route.snapshotJson = null;
        FavoriteValidation.route(route);
    }

    @Test public void trimsNamesAndCountsUnicodeCharacters() {
        assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.title("   "));
        assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.title("가".repeat(51)));
        String emojiName = "🌙".repeat(50);
        assertEquals(emojiName, FavoriteValidation.title(emojiName));
    }

    @Test public void rejectsInvalidCoordinatesAndUnknownProfile() {
        for (double coordinate : new double[]{Double.NaN, Double.POSITIVE_INFINITY, 90.1, -90.1}) {
            FavoriteRoute route = valid();
            route.originLatitude = coordinate;
            assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(route));
        }
        FavoriteRoute longitude = valid();
        longitude.destinationLongitude = 180.1;
        assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(longitude));
        FavoriteRoute profile = valid();
        profile.preferredProfile = "drive";
        assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(profile));
    }

    @Test public void rejectsExternalEndpointsAndNestedTmapPayloads() {
        FavoriteRoute route = valid();
        route.originSource = "tmap";
        assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(route));
        route.originSource = "user_coordinate";
        for (String snapshot : new String[]{"{\"routes\":[{\"provider\":\"TMAP\"}]}", "{\"tmapRaw\":{}}"}) {
            route.snapshotJson = snapshot;
            assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(route));
        }
    }

    @Test public void rejectsBrokenOrNonObjectSnapshots() {
        FavoriteRoute route = valid();
        for (String snapshot : new String[]{"", "{", "[]", "null", "{} trailing"}) {
            route.snapshotJson = snapshot;
            assertThrows(IllegalArgumentException.class, () -> FavoriteValidation.route(route));
        }
    }
}
