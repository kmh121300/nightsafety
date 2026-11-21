package kr.ac.tukorea.nightsafety.favorites;

import android.content.Context;
import android.os.Looper;
import androidx.room.Room;
import java.util.List;
import java.util.NoSuchElementException;

/** One owner per Activity; queue all calls and close on that owner's background executor. */
public final class FavoriteStore implements AutoCloseable {
    private final FavoriteDatabase database;

    public FavoriteStore(Context context) {
        database = Room.databaseBuilder(context.getApplicationContext(), FavoriteDatabase.class,
                "night-safety-favorites.db").build();
    }

    public List<FavoriteRoute> list() {
        backgroundOnly();
        return database.favorites().list();
    }

    public FavoriteRoute get(long id) {
        backgroundOnly();
        return database.favorites().get(id);
    }

    /** id=0 inserts; an existing id replaces the snapshot after successful validation. */
    public long save(FavoriteRoute route) {
        backgroundOnly();
        FavoriteValidation.route(route);
        return database.runInTransaction(() -> {
            FavoriteDao dao = database.favorites();
            long now = System.currentTimeMillis();
            route.title = FavoriteValidation.title(route.title);
            if (route.id == 0) {
                route.createdAt = now;
                route.modifiedAt = now;
                route.savedAt = now;
                return dao.insert(route);
            }
            FavoriteRoute previous = dao.get(route.id);
            if (previous == null) throw new NoSuchElementException("저장된 경로를 찾을 수 없습니다.");
            route.createdAt = previous.createdAt;
            route.modifiedAt = previous.modifiedAt;
            route.savedAt = now;
            dao.update(route);
            return route.id;
        });
    }

    /** A profile edit retains the old snapshot; caller must re-search before claiming it matches. */
    public void rename(long id, String title, String profile) {
        backgroundOnly();
        String trimmed = FavoriteValidation.title(title);
        FavoriteValidation.profile(profile);
        database.runInTransaction(() -> {
            if (database.favorites().rename(id, trimmed, profile, System.currentTimeMillis()) != 1) {
                throw new NoSuchElementException("저장된 경로를 찾을 수 없습니다.");
            }
        });
    }

    public void delete(long id) {
        backgroundOnly();
        database.runInTransaction(() -> {
            if (database.favorites().delete(id) != 1) {
                throw new NoSuchElementException("저장된 경로를 찾을 수 없습니다.");
            }
        });
    }

    @Override public void close() {
        backgroundOnly();
        database.close();
    }

    private static void backgroundOnly() {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            throw new IllegalStateException("즐겨찾기 DB는 백그라운드에서 호출해 주세요.");
        }
    }
}
