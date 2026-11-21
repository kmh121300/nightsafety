package kr.ac.tukorea.nightsafety.favorites;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;
import java.util.Iterator;
import java.util.Locale;

final class FavoriteValidation {
    private FavoriteValidation() { }

    static String title(String title) {
        if (title == null) throw new IllegalArgumentException("즐겨찾기 이름을 입력해 주세요.");
        String trimmed = title.trim();
        int length = trimmed.codePointCount(0, trimmed.length());
        if (length < 1 || length > 50) throw new IllegalArgumentException("이름은 1~50자로 입력해 주세요.");
        return trimmed;
    }

    static void profile(String profile) {
        if (!"fast".equals(profile) && !"safe".equals(profile)
                && !"balanced".equals(profile) && !"pedestrian".equals(profile)) {
            throw new IllegalArgumentException("지원하지 않는 경로 유형입니다.");
        }
    }

    static void route(FavoriteRoute route) {
        if (route == null || route.id < 0) throw new IllegalArgumentException("잘못된 즐겨찾기입니다.");
        title(route.title);
        profile(route.preferredProfile);
        coordinate(route.originLatitude, 90);
        coordinate(route.destinationLatitude, 90);
        coordinate(route.originLongitude, 180);
        coordinate(route.destinationLongitude, 180);
        source(route.originSource);
        source(route.destinationSource);
        if (route.originLabel == null || route.destinationLabel == null) {
            throw new IllegalArgumentException("장소 이름이 필요합니다.");
        }
        if (route.snapshotJson != null) {
            try {
                JSONTokener parser = new JSONTokener(route.snapshotJson);
                Object snapshot = parser.nextValue();
                if (!(snapshot instanceof JSONObject) || parser.nextClean() != 0) {
                    throw new JSONException("Snapshot must be a JSON object");
                }
                rejectTmap(snapshot);
            } catch (JSONException error) {
                throw new IllegalArgumentException("저장할 경로 데이터가 올바르지 않습니다.", error);
            }
        }
    }

    private static void coordinate(double value, double limit) {
        if (!Double.isFinite(value) || Math.abs(value) > limit) {
            throw new IllegalArgumentException("좌표 범위가 올바르지 않습니다.");
        }
    }

    private static void source(String source) {
        if (!"user_coordinate".equals(source) && !"osm".equals(source)) {
            throw new IllegalArgumentException("사용자 좌표 또는 OSM 장소만 저장할 수 있습니다.");
        }
    }

    private static void rejectTmap(Object value) throws JSONException {
        if (value instanceof JSONObject) {
            JSONObject object = (JSONObject) value;
            Iterator<String> keys = object.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                rejectTmap(key);
                rejectTmap(object.get(key));
            }
        } else if (value instanceof JSONArray) {
            JSONArray array = (JSONArray) value;
            for (int i = 0; i < array.length(); i++) rejectTmap(array.get(i));
        } else if (value instanceof String
                && ((String) value).toLowerCase(Locale.ROOT).contains("tmap")) {
            throw new IllegalArgumentException("TMAP 응답은 즐겨찾기에 영구 저장할 수 없습니다.");
        }
    }
}
